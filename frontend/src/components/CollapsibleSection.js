import React, { useState } from 'react';

/**
 * Unified accessible collapsible panel used across Dashboard sections
 * (Security Evidence & SIEM Correlation, Service Access Directory).
 * Preserves children mounted state to avoid remounts or duplicate API calls.
 */
function CollapsibleSection({
  id,
  title,
  subtitle,
  summaryPills,
  expandLabel,
  collapseLabel,
  expandAriaLabel,
  collapseAriaLabel,
  defaultExpanded = false,
  children,
}) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const panelId = `${id}-panel`;
  const headingId = `${id}-heading`;
  const buttonId = `${id}-toggle`;

  const toggleExpanded = () => {
    setIsExpanded((prev) => !prev);
  };

  const resolvedAriaLabel = isExpanded
    ? collapseAriaLabel || collapseLabel
    : expandAriaLabel || expandLabel;

  return (
    <section className="collapsible-section" aria-labelledby={headingId}>
      <div className="collapsible-header">
        <div className="collapsible-header-main">
          <div className="collapsible-title-row">
            <h3 id={headingId} className="collapsible-title">
              {title}
            </h3>
            {summaryPills && (
              <div className="collapsible-summary-pills">{summaryPills}</div>
            )}
          </div>
          {subtitle && <p className="collapsible-subtitle">{subtitle}</p>}
        </div>

        <button
          id={buttonId}
          type="button"
          className="collapsible-toggle-btn"
          aria-expanded={isExpanded}
          aria-controls={panelId}
          aria-label={resolvedAriaLabel}
          onClick={toggleExpanded}
        >
          <span>{isExpanded ? collapseLabel : expandLabel}</span>
          <span
            className={`collapsible-chevron ${isExpanded ? 'is-open' : ''}`}
            aria-hidden="true"
          >
            {isExpanded ? '▲' : '▼'}
          </span>
        </button>
      </div>

      <div
        id={panelId}
        data-testid={panelId}
        role="region"
        aria-labelledby={headingId}
        hidden={!isExpanded}
        className={`collapsible-content ${isExpanded ? 'is-open' : 'is-collapsed'}`}
      >
        {children}
      </div>
    </section>
  );
}

export default CollapsibleSection;
