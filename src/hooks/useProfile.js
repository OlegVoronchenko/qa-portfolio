/**
 * Profile Data Hook
 *
 * Returns the parsed profile.json object containing all personal,
 * experience, skills, and contact data that drives every section
 * of the portfolio site. src/data/profile.json is the single,
 * Git-tracked canonical source (see scripts/validate_profile.py) —
 * components should never hardcode personal information.
 */
import profileData from '../data/profile.json'

/** @returns {object} Full profile data from profile.json */
export function useProfile() {
  return profileData
}
