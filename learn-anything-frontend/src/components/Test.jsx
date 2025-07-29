import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

const md = `
Inline math: $f(n) = O(n^2)$

Block math:

$$
f(n) = 3n^2 + 5n + 2
$$
`;

export default function MathTest() {
  return (
    <div className="prose max-w-none p-6">
      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
        {md}
      </ReactMarkdown>
    </div>
  );
}
