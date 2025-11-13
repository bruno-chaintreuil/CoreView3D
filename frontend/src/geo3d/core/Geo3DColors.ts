export const LITHOLOGY_COLORS: Record<string, number> = {
  Overburden: 0x8B7355,
  Weathered_Granite: 0xDAA520,
  Weathered_Schist: 0xCD853F,
  Mineralized_Zone: 0x00CED1,
  High_Grade_Ore: 0xFF4500,
  Fresh_Granite: 0x708090,
  Fresh_Schist: 0x556B2F,
}

export function getDefaultDrillholeColor(id: string): number {
  const hash = id.split('').reduce((a, b) => a + b.charCodeAt(0), 0)
  const hue = hash % 360
  return hslToHex(hue, 70, 50)
}

function hslToHex(h: number, s: number, l: number): number {
  s /= 100
  l /= 100
  const a = s * Math.min(l, 1 - l)
  const f = (n: number) => {
    const k = (n + h / 30) % 12
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
    return Math.round(255 * color)
  }
  return (f(0) << 16) | (f(8) << 8) | f(4)
}