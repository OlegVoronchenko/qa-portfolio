/**
 * Requirements Data Hook
 *
 * Provides access to the requirements.json bundle generated from
 * docs/requirements/REQ-*.md files. Used by TestResults component
 * to display clickable requirement and acceptance criteria badges
 * with expandable detail panels.
 *
 * Data is imported statically at build time — no runtime API calls.
 */
import requirementsData from '../data/requirements.json'

/** @returns {object} All requirements keyed by REQ ID (e.g. "REQ-001") */
export function useRequirements() {
  return requirementsData
}

/**
 * Look up a requirement by its ID.
 * @param {string} reqId - e.g. "REQ-001"
 * @returns {{ id: string, title: string, requirement: string, acceptance_criteria: object } | null}
 */
export function getRequirement(reqId) {
  return requirementsData[reqId] ?? null
}

/**
 * Look up an acceptance criterion within a requirement.
 * @param {string} reqId - e.g. "REQ-001"
 * @param {string} acId - e.g. "AC-001-3"
 * @returns {{ id: string, title: string, description: string } | null}
 */
export function getAcceptanceCriterion(reqId, acId) {
  const req = getRequirement(reqId)
  return req?.acceptance_criteria[acId] ?? null
}
