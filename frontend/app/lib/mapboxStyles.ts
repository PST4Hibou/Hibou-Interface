export const MAPBOX_STYLE_IDS = [
  'standard',
  'streets',
  'outdoors',
  'light',
  'dark',
  'satellite',
  'satellite-streets',
  'navigation-day',
  'navigation-night',
] as const

export type MapboxStyleId = (typeof MAPBOX_STYLE_IDS)[number]

const STYLE_URLS: Record<MapboxStyleId, string> = {
  standard: 'mapbox://styles/mapbox/standard',
  streets: 'mapbox://styles/mapbox/streets-v12',
  outdoors: 'mapbox://styles/mapbox/outdoors-v12',
  light: 'mapbox://styles/mapbox/light-v11',
  dark: 'mapbox://styles/mapbox/dark-v11',
  satellite: 'mapbox://styles/mapbox/satellite-v9',
  'satellite-streets': 'mapbox://styles/mapbox/satellite-streets-v12',
  'navigation-day': 'mapbox://styles/mapbox/navigation-day-v1',
  'navigation-night': 'mapbox://styles/mapbox/navigation-night-v1',
}

export function isMapboxStyleId(v: string): v is MapboxStyleId {
  return (MAPBOX_STYLE_IDS as readonly string[]).includes(v)
}

/** Mapbox GL `style` URL; defaults to satellite when missing or unknown. */
export function mapStyleUrl(styleId: string | null | undefined): string {
  if (styleId && isMapboxStyleId(styleId)) {
    return STYLE_URLS[styleId]
  }
  return STYLE_URLS.satellite
}
