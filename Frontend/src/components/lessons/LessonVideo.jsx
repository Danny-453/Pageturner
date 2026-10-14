function getVideoSource(videoUrl) {
  try {
    const url = new URL(videoUrl);
    if (url.protocol !== 'https:') return { type: 'link', url: videoUrl };

    const host = url.hostname.toLowerCase().replace(/^www\./, '');
    let youtubeId = null;
    if (host === 'youtu.be') {
      youtubeId = url.pathname.split('/').filter(Boolean)[0];
    } else if (host === 'youtube.com' || host === 'm.youtube.com') {
      youtubeId = url.searchParams.get('v')
        || url.pathname.match(/^\/(?:embed|shorts|live)\/([^/]+)/)?.[1];
    }
    if (youtubeId && /^[A-Za-z0-9_-]{11}$/.test(youtubeId)) {
      return { type: 'embed', url: `https://www.youtube-nocookie.com/embed/${youtubeId}` };
    }

    if (host === 'vimeo.com' || host === 'player.vimeo.com') {
      const vimeoId = url.pathname.match(/\/(?:video\/)?(\d+)\/?$/)?.[1];
      if (vimeoId) return { type: 'embed', url: `https://player.vimeo.com/video/${vimeoId}` };
    }

    if (/\.(?:mp4|webm|ogg)$/i.test(url.pathname)) {
      return { type: 'file', url: url.href };
    }
    return { type: 'link', url: url.href };
  } catch {
    return { type: 'link', url: videoUrl };
  }
}

export default function LessonVideo({ url, title }) {
  if (!url) return null;

  const source = getVideoSource(url);
  return (
    <section className="card card-pad" style={{ marginTop: 24 }}>
      <h2 style={{ marginTop: 0 }}>Lesson video</h2>
      {source.type === 'embed' && (
        <div style={{ aspectRatio: '16 / 9', width: '100%' }}>
          <iframe
            src={source.url}
            title={`Lesson video: ${title}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerPolicy="strict-origin-when-cross-origin"
            allowFullScreen
            loading="lazy"
            style={{ width: '100%', height: '100%', border: 0, borderRadius: 8 }}
          />
        </div>
      )}
      {source.type === 'file' && (
        <video controls preload="metadata" style={{ display: 'block', width: '100%', borderRadius: 8 }}>
          <source src={source.url} />
          Your browser does not support this video format.
        </video>
      )}
      {source.type === 'link' && (
        <a href={source.url} target="_blank" rel="noopener noreferrer">
          Watch {title} in a new tab
        </a>
      )}
    </section>
  );
}
