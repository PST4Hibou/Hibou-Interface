export interface SystemSettings {
  latitude: number | undefined
  longitude: number | undefined
  angle_from_longitude: number | undefined
  map_zoom: number | undefined
  /** Map tilt in degrees (Mapbox GL: 0–85). */
  map_pitch: number | undefined
  /** Extrude Mapbox building footprints where the style provides them (streets-like sources). */
  map_3d_buildings: boolean | undefined
  /** Map style key, e.g. `satellite`, `dark`, `standard`. */
  mapbox_style: string | undefined
}
