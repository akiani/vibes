export const metadata = {
  title: 'Todo App',
  description: 'A beautiful and simple todo app built with Next.js',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
