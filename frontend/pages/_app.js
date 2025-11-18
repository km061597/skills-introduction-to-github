import '../styles/globals.css'
import SkipLinks from '../components/SkipLinks'

export default function App({ Component, pageProps }) {
  return (
    <>
      <SkipLinks />
      <Component {...pageProps} />
    </>
  )
}
