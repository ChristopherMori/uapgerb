import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type {Preset} from '@docusaurus/preset-classic';

const config: Config = {
  title: 'UAP Gerb Transcripts',
  tagline: 'Catalog, transcripts, and links',

  // For GitHub Pages
  url: 'https://christophermori.github.io',
  baseUrl: '/uapgerb/',
  organizationName: 'ChristopherMori',   // GitHub user/org
  projectName: 'uapgerb',                // repo name
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {defaultLocale: 'en', locales: ['en']},

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.ts'),
          editUrl: 'https://github.com/ChristopherMori/uapgerb/tree/main/',
          showLastUpdateTime: true,
          includeCurrentVersion: true,
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'UAP Gerb',
      items: [
        {type: 'docSidebar', sidebarId: 'docsSidebar', position: 'left', label: 'Docs'},
        {href: 'https://github.com/ChristopherMori/uapgerb', label: 'GitHub', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {title: 'Links', items: [{label: 'GitHub', to: 'https://github.com/ChristopherMori/uapgerb'}]},
      ],
      copyright: `© ${new Date().getFullYear()} UAP Gerb`,
    },
    prism: {theme: prismThemes.github, darkTheme: prismThemes.dracula},
  },
};

export default config;
