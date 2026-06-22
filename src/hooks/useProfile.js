/**
 * Profile Data Hook
 *
 * Returns the parsed profile.json object containing all personal,
 * experience, skills, and contact data that drives every section
 * of the portfolio site. Data originates from either the CV parser
 * or profile.default.json — components should never hardcode
 * personal information.
 */
import profileData from '../data/profile.json'

/** @returns {object} Full profile data from profile.json */
export function useProfile() {
  return profileData
}
