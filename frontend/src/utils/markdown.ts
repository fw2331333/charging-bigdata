import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
})

const defaultLinkOpen =
  md.renderer.rules.link_open ??
  ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options))

md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  if (token.attrIndex('target') < 0) token.attrPush(['target', '_blank'])
  if (token.attrIndex('rel') < 0) token.attrPush(['rel', 'noopener noreferrer'])
  return defaultLinkOpen(tokens, idx, options, env, self)
}

export function renderMarkdown(text: string): string {
  if (!text) return ''
  return DOMPurify.sanitize(md.render(text), {
    ADD_ATTR: ['target', 'rel'],
  })
}
