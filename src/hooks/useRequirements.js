import requirementsData from '../data/requirements.json'

export function useRequirements() {
  return requirementsData
}

export function getRequirement(reqId) {
  return requirementsData[reqId] ?? null
}

export function getAcceptanceCriterion(reqId, acId) {
  const req = getRequirement(reqId)
  return req?.acceptance_criteria[acId] ?? null
}
