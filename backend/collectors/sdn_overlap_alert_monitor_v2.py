import argparse
import json
import math
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

try:
    import msvcrt

    def lock_handle(handle):
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)

    def unlock_handle(handle):
        try:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
except ImportError:
    import fcntl

    def lock_handle(handle):
        handle.seek(0)
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def unlock_handle(handle):
        try:
            handle.seek(0)
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass

from sdn_auto_alert_monitor import valid_sample, make_alert
from sdn_alert_publisher import already_exists, http_json, LOGSTASH_URL

BASE = 'http://127.0.0.1:9200'
INDEX = 'sdnflowguard-events-*'
STATE_DIR = Path(__file__).resolve().parent / 'state'


def parse_ts(value):
    import re

    raw = str(value).strip()

    # Convert nanoseconds to microseconds for Python 3.10.
    raw = re.sub(
        r'(\.\d{6})\d+(?=Z|[+-]\d{2}:\d{2}|$)',
        r'\1',
        raw
    )

    parsed = datetime.fromisoformat(
        raw.replace('Z', '+00:00')
    )

    if parsed.tzinfo is None:
        raise ValueError("Timestamp must contain timezone")

    return parsed.astimezone(timezone.utc)


def request_json(method, url, payload=None):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    if method == 'POST' and data is None:
        data = b''
    request = Request(url, data=data,
                      headers={'Content-Type': 'application/json'}, method=method)
    with urlopen(request, timeout=20) as response:
        body = response.read()
        return json.loads(body) if body else {}


def fetch_window(watermark, minutes, days):
    start = parse_ts(watermark) - timedelta(minutes=minutes)
    pit = request_json('POST', f'{BASE}/{INDEX}/_pit?keep_alive=2m')['id']
    documents = []
    cursor = None
    try:
        for page in range(51):
            if page == 50:
                raise RuntimeError('More than 10000 records in scan; checkpoint unchanged.')
            query = {
                'size': 200,
                'pit': {'id': pit, 'keep_alive': '2m'},
                'sort': [
                    {'@timestamp': {'order': 'asc', 'format': 'strict_date_optional_time_nanos'}},
                    {'event_id.keyword': {'order': 'asc'}}
                ],
                '_source': ['@timestamp', 'event_id', 'switch_id', 'port_number',
                            'rx_pps', 'tx_pps', 'sample_seconds'],
                'query': {'bool': {'filter': [
                    {'term': {'event_type.keyword': 'sdn_port_traffic'}},
                    {'exists': {'field': 'event_id.keyword'}},
                    {'range': {'@timestamp': {'gte': start.isoformat()}}},
                    {'range': {'@timestamp': {'gte': f'now-{days}d'}}}
                ]}}
            }
            if cursor is not None:
                query['search_after'] = cursor
            response = request_json('POST', f'{BASE}/_search', query)
            pit = response.get('pit_id', pit)
            hits = response.get('hits', {}).get('hits', [])
            documents.extend(hits)
            if len(hits) < 200:
                break
            cursor = hits[-1]['sort']
    finally:
        try:
            request_json('DELETE', f'{BASE}/_pit', {'id': pit})
        except Exception as error:
            print('[WARN] PIT cleanup:', error, flush=True)
    return documents


def doc_id(hit):
    return str(hit['_index']) + ':' + str(hit['_id'])


def build_candidates(hits, new_ids, threshold, consecutive):
    by_port = {}
    for hit in hits:
        sample = valid_sample(hit)
        if sample is None:
            continue
        switch, port, _, when, rx, tx, interval = sample
        by_port.setdefault((switch, port), []).append((when, doc_id(hit), hit, sample))

    results = []
    for key, records in sorted(by_port.items()):
        records.sort(key=lambda row: (row[0], row[1]))
        episode = []
        last_time = None

        def finish_episode():
            if len(episode) >= consecutive and any(r[1] in new_ids for r in episode):
                trigger = episode[consecutive - 1]
                results.append((trigger[2], trigger[3]))

        for row in records:
            when, _, _, sample = row
            interval = sample[6]
            gap = None if last_time is None else (when - last_time).total_seconds()
            if gap is not None and (gap <= 0 or gap > max(45.0, interval * 2.5)):
                finish_episode()
                episode = []
            if max(sample[4], sample[5]) >= threshold:
                episode.append(row)
            else:
                finish_episode()
                episode = []
            last_time = when
        finish_episode()
    return results


def write_state(path, state):
    temp = path.with_suffix('.tmp')
    with open(temp, 'w', encoding='utf-8') as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def lock_file(path):
    handle = open(path, 'a+b')
    handle.seek(0, os.SEEK_END)
    if handle.tell() == 0:
        handle.write(b'0')
        handle.flush()
    handle.seek(0)
    try:
        lock_handle(handle)
    except OSError:
        handle.close()
        raise RuntimeError('Another V2 monitor is running with this configuration.')
    return handle


def init_state(state_path, legacy_path, args):
    if state_path.exists():
        with open(state_path, encoding='utf-8') as handle:
            state = json.load(handle)
        if (state.get('version') != 2 or
                state.get('threshold_pps') != args.threshold_pps or
                state.get('consecutive') != args.consecutive or
                state.get('window_minutes') != args.window_minutes):
            raise RuntimeError('V2 checkpoint configuration mismatch; unchanged.')
        print('[RESUME V2] Checkpoint loaded', flush=True)
        return state
    if not legacy_path.exists():
        raise RuntimeError('V1 checkpoint is missing. No bootstrap performed.')
    with open(legacy_path, encoding='utf-8') as handle:
        old = json.load(handle)
    if old.get('version') != 1 or old.get('threshold_pps') != args.threshold_pps or old.get('consecutive') != args.consecutive:
        raise RuntimeError('V1 checkpoint does not match configuration.')
    cursor = old.get('cursor')
    if not cursor or not isinstance(cursor, list):
        raise RuntimeError('V1 cursor is empty; cannot migrate safely.')
    watermark = parse_ts(cursor[0])
    hits = fetch_window(watermark.isoformat(), args.window_minutes, args.lookback_days)
    # Legacy search_after timestamps may be rounded to milliseconds.
    # Recover the precise last event timestamp when its ID is still indexed.
    for hit in hits:
        if (hit.get('_source') or {}).get('event_id') == cursor[1]:
            watermark = max(watermark, parse_ts(hit['_source']['@timestamp']))
            break
    seen = {doc_id(h): h['_source']['@timestamp'] for h in hits
            if parse_ts(h['_source']['@timestamp']) <= watermark}
    state = {
        'version': 2,
        'threshold_pps': args.threshold_pps,
        'consecutive': args.consecutive,
        'window_minutes': args.window_minutes,
        'watermark': watermark.isoformat(),
        'seen_ids': seen,
        'notified': {},
        'updated_at_utc': datetime.now(timezone.utc).isoformat(),
    }
    write_state(state_path, state)
    print(f'[MIGRATED] V1 cursor preserved; {len(seen)} existing documents marked as seen', flush=True)
    print('[INFO] V1 checkpoint not modified', flush=True)
    return state


def self_test():
    def hit(doc_id_value, stamp, pps):
        return {
            '_index': 'test-index', '_id': doc_id_value,
            '_source': {'@timestamp': stamp, 'event_id': doc_id_value,
                        'switch_id': 'of:test', 'port_number': 1, 'rx_pps': pps,
                        'tx_pps': pps, 'sample_seconds': 10.0}
        }
    old_a = hit('a', '2026-10-31T18:00:00Z', 6)
    old_b = hit('b', '2026-10-31T18:00:20Z', 0)
    late = hit('late', '2026-10-31T18:00:10Z', 7)
    results = build_candidates([old_a, late, old_b], {'test-index:late'}, 4, 2)
    repeat = build_candidates([old_a, late, old_b], set(), 4, 2)
    assert len(results) == 1, f'Expected 1 late-data candidate, got {len(results)}'
    assert len(repeat) == 0, f'Expected no replay, got {len(repeat)}'
    print('SELF TEST PASS: late-arriving sample detected, unchanged data not replayed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--poll-seconds', type=int, default=5)
    parser.add_argument('--cycles', type=int, default=3)
    parser.add_argument('--lookback-days', type=int, default=7)
    parser.add_argument('--window-minutes', type=int, default=10)
    parser.add_argument('--threshold-pps', type=float, default=4.0)
    parser.add_argument('--consecutive', type=int, default=2)
    parser.add_argument('--publish-test-alerts', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if (args.poll_seconds < 3 or args.cycles < 0 or
            not 1 <= args.lookback_days <= 7 or
            not 1 <= args.window_minutes <= 60 or
            not math.isfinite(args.threshold_pps) or args.threshold_pps <= 0 or
            args.consecutive < 2):
        parser.error('Invalid monitor parameters')

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    mode = 'publish' if args.publish_test_alerts else 'dry'
    tag = format(args.threshold_pps, 'g').replace('.', 'p')
    base_name = f'auto_{mode}_t{tag}_c{args.consecutive}'
    state_path = STATE_DIR / (base_name + '_v2.json')
    legacy_path = STATE_DIR / (base_name + '.json')
    lock = lock_file(STATE_DIR / (base_name + '_v2.lock'))
    try:
        state = init_state(state_path, legacy_path, args)
        print('=== OVERLAP ALERT MONITOR V2 ===')
        print('Mode:', mode.upper(), '| Window:', args.window_minutes, 'min')
        print('Checkpoint:', state_path)
        cycle = 0
        while args.cycles == 0 or cycle < args.cycles:
            cycle += 1
            hits = fetch_window(state['watermark'], args.window_minutes, args.lookback_days)
            previous_seen = state['seen_ids']
            new_ids = {doc_id(hit) for hit in hits if doc_id(hit) not in previous_seen}
            old_watermark = parse_ts(state['watermark'])
            late_count = sum(
                1 for hit in hits
                if doc_id(hit) in new_ids and
                parse_ts(hit['_source']['@timestamp']) < old_watermark
            )
            candidates = build_candidates(hits, new_ids, args.threshold_pps, args.consecutive)
            notified = state['notified']
            created = 0
            for trigger, sample in candidates:
                event = make_alert(trigger, sample, args.threshold_pps, args.consecutive)
                key = event['alert_key']
                if key in notified:
                    continue
                print('[CANDIDATE] Port={} Peak={:.3f} PPS'.format(
                    event['port_number'], event['peak_pps']), flush=True)
                if args.publish_test_alerts:
                    if already_exists(key):
                        print('  [SKIP] Already indexed', flush=True)
                    else:
                        http_json(LOGSTASH_URL, event)
                        confirmed = False
                        for _ in range(10):
                            time.sleep(1)
                            if already_exists(key):
                                confirmed = True
                                break
                        if not confirmed:
                            raise RuntimeError('Alert not indexed. V2 checkpoint unchanged.')
                        print('  [SENT] Verified in Elasticsearch', flush=True)
                else:
                    print('  [DRY RUN] No alert sent', flush=True)
                notified[key] = sample[2]
                created += 1

            max_seen = max(
                [old_watermark] + [parse_ts(h['_source']['@timestamp']) for h in hits]
            )
            cutoff = max_seen - timedelta(minutes=args.window_minutes, seconds=60)
            state['seen_ids'] = {
                doc_id(h): h['_source']['@timestamp'] for h in hits
                if parse_ts(h['_source']['@timestamp']) >= cutoff
            }
            state['notified'] = {
                key: stamp for key, stamp in notified.items()
                if parse_ts(stamp) >= cutoff
            }
            state['watermark'] = max_seen.isoformat()
            state['updated_at_utc'] = datetime.now(timezone.utc).isoformat()
            write_state(state_path, state)
            print('[POLL] Cycle={} New={} Late={} Candidates={}'.format(
                cycle, len(new_ids), late_count, created), flush=True)
            if args.cycles == 0 or cycle < args.cycles:
                time.sleep(args.poll_seconds)
        print('No ONOS flow rules were changed.')
        print('Overlap Monitor V2 finished.')
    finally:
        try:
            unlock_handle(lock)
        finally:
            lock.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nMonitor stopped safely.')
