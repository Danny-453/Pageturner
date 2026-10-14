import ReactMarkdown from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkLegacyMath from './remarkLegacyMath';
import 'katex/dist/katex.min.css';

export default function MarkdownContent({ children, className = '' }) {
  return (
    <div className={`markdown-content ${className}`.trim()}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath, remarkLegacyMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          img: ({ alt, src, title }) => (
            <img
              src={src}
              alt={alt || ''}
              title={title}
              loading="lazy"
              decoding="async"
              referrerPolicy="no-referrer"
            />
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
