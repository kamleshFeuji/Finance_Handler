import { request, writeJSON } from './client.js'

export async function getProfile(signal) {
  return (await request('profile/', { signal })).profile
}

export async function saveProfile(profile) {
  return (await writeJSON('profile/', 'PUT', profile)).profile
}
