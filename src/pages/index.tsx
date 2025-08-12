import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function Home(): JSX.Element {
  return (
    <Layout title="UAP Gerb Transcripts" description="Catalog, transcripts, and links">
      <main className="container margin-vert--lg">
        <h1>UAP Gerb Transcripts</h1>
        <p>Browse transcripts, subtitles, and links for curated videos.</p>
        <p>
          <Link className="button button--primary button--lg" to="/docs/category/videos">
            Browse Videos
          </Link>
        </p>
      </main>
    </Layout>
  );
}
