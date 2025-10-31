'use client';

import { useState } from 'react';

export default function SlugForm({ initialSlug }: { initialSlug?: string }) {
  const [slug, setSlug] = useState(initialSlug || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (slug.trim()) {
      window.location.href = `/?slug=${encodeURIComponent(slug.trim())}`;
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
          placeholder="記事のSlugを入力"
          style={{
            flex: 1,
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '1rem'
          }}
        />
        <button
          type="submit"
          style={{
            padding: '0.5rem 1.5rem',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            cursor: 'pointer'
          }}
        >
          送信
        </button>
      </div>
    </form>
  );
}
