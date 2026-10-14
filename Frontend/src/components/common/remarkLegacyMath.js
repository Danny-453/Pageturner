function isLatexMath(value) {
  return /\\[A-Za-z]+|[=<>]|(?:\b[A-Za-z0-9]+\s*[_^])/.test(value);
}

function displayMathValue(value) {
  const trimmed = value.trim();
  const latexBracketMatch = trimmed.match(/^\\\[([\s\S]+?)\\\]$/);
  if (latexBracketMatch) return latexBracketMatch[1].trim();

  const bracketMatch = trimmed.match(/^\[([\s\S]+)\]$/);
  if (bracketMatch && isLatexMath(bracketMatch[1])) return bracketMatch[1].trim();
  return null;
}

function inlineMathNodes(value) {
  const nodes = [];
  const delimiters = /\\\(([\s\S]+?)\\\)|\(([^()\n]*\\[A-Za-z][^()\n]*)\)/g;
  let lastIndex = 0;

  for (const match of value.matchAll(delimiters)) {
    const math = match[1] ?? match[2];
    if (!math.trim()) continue;
    if (match.index > lastIndex) {
      nodes.push({ type: 'text', value: value.slice(lastIndex, match.index) });
    }
    nodes.push({ type: 'inlineMath', value: math.trim() });
    lastIndex = match.index + match[0].length;
  }

  if (!nodes.length) return null;
  if (lastIndex < value.length) {
    nodes.push({ type: 'text', value: value.slice(lastIndex) });
  }
  return nodes;
}

function transformChildren(parent) {
  if (!Array.isArray(parent.children)) return;

  parent.children = parent.children.flatMap((child) => {
    if (child.type === 'paragraph' && child.children?.length === 1 && child.children[0].type === 'text') {
      const math = displayMathValue(child.children[0].value);
      if (math) return [{ type: 'math', value: math }];
    }

    if (child.type === 'text') {
      return inlineMathNodes(child.value) || [child];
    }

    if (!['inlineCode', 'code', 'link', 'linkReference', 'image', 'imageReference'].includes(child.type)) {
      transformChildren(child);
    }
    return [child];
  });
}

export default function remarkLegacyMath() {
  return transformChildren;
}
