export const metadata = {
  title: 'タグ選択システム',
  description: 'AWS Bedrock Claude Haiku版',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  )
}
