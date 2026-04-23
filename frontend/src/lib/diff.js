import { diffWordsWithSpace } from "diff";

/**
 * Compute a word-level diff between two strings.
 *
 * @param {string} original
 * @param {string} humanized
 * @returns {Array<{type: "equal" | "added" | "removed", text: string}>}
 */
export function computeDiff(original, humanized) {
  const parts = diffWordsWithSpace(original ?? "", humanized ?? "");
  return parts.map((p) => ({
    type: p.added ? "added" : p.removed ? "removed" : "equal",
    text: p.value,
  }));
}

/**
 * Summary stats for a diff.
 *
 * @param {Array<{type: string, text: string}>} parts
 * @returns {{added: number, removed: number, equal: number, changeRatio: number}}
 */
export function diffStats(parts) {
  let added = 0;
  let removed = 0;
  let equal = 0;
  for (const p of parts) {
    const n = p.text.length;
    if (p.type === "added") added += n;
    else if (p.type === "removed") removed += n;
    else equal += n;
  }
  const total = added + removed + equal;
  const changeRatio = total === 0 ? 0 : (added + removed) / total;
  return { added, removed, equal, changeRatio };
}
