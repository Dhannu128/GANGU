'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import {
  ArrowRight, BadgeCheck, Check, ChevronDown, Eye, Globe2,
  ListChecks, LockKeyhole, Menu, Mic, Pause, Play, Search, ShieldCheck,
  ShoppingBasket, Smartphone, Users,
} from 'lucide-react'
import Logo from '@/components/Logo'
import { useGANGUStore } from '@/lib/store'

const SAMPLE_REQUESTS = [
  {
    label: 'Morning basics', request: '“Do kilo atta aur ek litre doodh”',
    result: '2 items understood', detail: 'Atta · 2 kg  /  Milk · 1 litre', note: 'Quantities retained',
  },
  {
    label: 'Breakfast help', request: '“Diabetes-friendly breakfast items”',
    result: 'Preference understood', detail: 'Lower-sugar options · final review required', note: 'Preference stays visible',
  },
  {
    label: 'Weekly repeat', request: '“Repeat my weekly grocery list”',
    result: 'Saved list prepared', detail: '6 browser-saved items · fully editable', note: 'No order is placed',
  },
] as const

const FEATURES = [
  {
    icon: Mic, title: 'Ask naturally',
    copy: 'Speak or type in Hindi, English, or Hinglish without learning commands or navigating complicated menus.',
    example: '“Aadha kilo dal aur chai patti”', result: 'Everyday words become a clear request',
    facts: ['Voice and text', 'Mixed-language input'], status: 'Available now', tone: 'saffron',
  },
  {
    icon: Search, title: 'Understand and compare',
    copy: 'GANGU structures quantities and preferences, then explains price, source, delivery estimate, and why an option was suggested.',
    example: '₹119 · estimated · source shown', result: 'Choices keep their context',
    facts: ['Ambiguity checked', 'Source labelled'], status: 'Provider dependent', tone: 'indigo',
  },
  {
    icon: BadgeCheck, title: 'Review and confirm',
    copy: 'Product, address, payment preference, and transaction mode appear together before any final confirmation.',
    example: 'Product · address · payment · mode', result: 'You make the final decision',
    facts: ['Review required', 'No automatic purchase'], status: 'Available now', tone: 'teal',
  },
  {
    icon: Eye, title: 'Accessible and secure',
    copy: 'Larger text, higher contrast, Firebase sign-in, and verified backend tokens reduce effort while protecting requests.',
    example: 'Google or phone OTP · comfort controls', result: 'Less strain and clearer control',
    facts: ['Saved preference', 'Verified sign-in'], status: 'Available now', tone: 'green',
  },
] as const

const HOW_STEPS = [
  { number: '01', title: 'Say or type your list', copy: 'Use everyday language—short and mixed-language requests are welcome.', traceTitle: 'Request captured', traceCopy: '“2 kg atta aur 1 litre doodh”', facts: ['Voice or text', 'Hindi · English · Hinglish'], icon: Mic, tone: 'saffron' },
  { number: '02', title: 'GANGU understands the need', copy: 'The request becomes a structured grocery list so you can spot mistakes before a search begins.', traceTitle: 'Intent understood', traceCopy: 'Atta · 2 kg  /  Milk · 1 litre', facts: ['Quantities retained', 'Ambiguity checked'], icon: ListChecks, tone: 'indigo' },
  { number: '03', title: 'Available choices are compared', copy: 'Results retain their price source, delivery estimate, and live or estimated status.', traceTitle: 'Options compared', traceCopy: '3 options · suggested ₹119', facts: ['Source labelled', 'Reason shown'], icon: Search, tone: 'teal' },
  { number: '04', title: 'You review and decide', copy: 'The important details appear together. Safe demo mode cannot place a real order.', traceTitle: 'Waiting for you', traceCopy: 'Final confirmation required', facts: ['Address checked', 'No automatic purchase'], icon: BadgeCheck, tone: 'green' },
] as const

const FAQS = [
  ['Does GANGU place orders automatically?', 'No. Every option reaches a final review first. Real purchasing remains disabled unless the backend safety switches and verified live provider data are deliberately enabled.'],
  ['Are prices and availability live?', 'Only when a connected provider returns verified live data. Estimated and demonstration results are labelled clearly and must not be treated as current store inventory.'],
  ['Which languages can I use?', 'You can speak or type in Hindi, English, or natural Hinglish. Speech recognition quality still depends on your browser and microphone.'],
  ['Can I use GANGU without voice?', 'Yes. Text input is always available, including when speech recognition is unsupported or microphone permission is denied.'],
  ['How does sign-in work?', 'Google sign-in and Indian mobile OTP use Firebase Authentication. The backend validates Firebase ID tokens before allowing protected requests.'],
  ['Is the Swiggy integration live?', 'Swiggy Builders Club approval has been received. Instamart MCP onboarding and credential provisioning are still in progress, so GANGU does not yet imply that Swiggy checkout is live.'],
] as const

export default function Home() {
  const auth = useGANGUStore((state) => state.auth)
  const settings = useGANGUStore((state) => state.settings)
  const updateSettings = useGANGUStore((state) => state.updateSettings)
  const [activeSample, setActiveSample] = useState(0)
  const [activeFeature, setActiveFeature] = useState(0)
  const [activeTrace, setActiveTrace] = useState(0)
  const [isTracePlaying, setIsTracePlaying] = useState(true)
  const [isTraceVisible, setIsTraceVisible] = useState(false)
  const howSectionRef = useRef<HTMLElement | null>(null)
  const destination = auth.isAuthenticated ? '/app' : '/signup'
  const actionLabel = auth.isAuthenticated ? 'Open GANGU' : 'Start with GANGU'
  const ActiveFeatureIcon = FEATURES[activeFeature].icon
  const ActiveTraceIcon = HOW_STEPS[activeTrace].icon

  useEffect(() => {
    document.documentElement.classList.toggle('gangu-large-text', settings.largerText)
    document.documentElement.classList.toggle('gangu-high-contrast', settings.higherContrast)
    return () => document.documentElement.classList.remove('gangu-large-text', 'gangu-high-contrast')
  }, [settings.largerText, settings.higherContrast])

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const followMotionPreference = () => {
      if (media.matches) setIsTracePlaying(false)
    }
    followMotionPreference()
    media.addEventListener('change', followMotionPreference)
    return () => media.removeEventListener('change', followMotionPreference)
  }, [])

  useEffect(() => {
    const section = howSectionRef.current
    if (!section || !('IntersectionObserver' in window)) {
      setIsTraceVisible(true)
      return
    }
    const observer = new IntersectionObserver(
      ([entry]) => setIsTraceVisible(entry.isIntersecting),
      { threshold: 0.35 },
    )
    observer.observe(section)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!isTracePlaying || !isTraceVisible) return
    const timer = window.setInterval(
      () => setActiveTrace((current) => (current + 1) % HOW_STEPS.length),
      3600,
    )
    return () => window.clearInterval(timer)
  }, [isTracePlaying, isTraceVisible])

  const selectTrace = (index: number) => {
    setActiveTrace(index)
    setIsTracePlaying(false)
  }

  return (
    <main className={`marketing-page home-page${settings.largerText ? ' home-page-large-text' : ''}${settings.higherContrast ? ' home-page-high-contrast' : ''}`}>
      <header className="home-header">
        <Link href="/" className="brand-lockup" aria-label="GANGU home">
          <Logo size={40} /><span><strong>GANGU</strong><small>grocery help · by voice</small></span>
        </Link>
        <nav className="desktop-home-nav" aria-label="Main navigation">
          <a href="#sample">Try a sample</a><a href="#features">Features</a><a href="#how">How it works</a><a href="#safety">Safety</a>
        </nav>
        <div className="header-actions">
          {!auth.isAuthenticated && <Link href="/signin" className="header-signin">Sign in</Link>}
          <Link href={destination} className="header-action">{auth.isAuthenticated ? 'Open GANGU' : 'Try GANGU'}</Link>
          <details className="mobile-home-menu">
            <summary aria-label="Open navigation"><Menu aria-hidden /></summary>
            <div className="mobile-home-panel">
              <div className="mobile-menu-title"><span>Explore GANGU</span></div>
              <a href="#sample" onClick={(event) => event.currentTarget.closest('details')?.removeAttribute('open')}>Try a sample</a>
              <a href="#features" onClick={(event) => event.currentTarget.closest('details')?.removeAttribute('open')}>Features</a>
              <a href="#how" onClick={(event) => event.currentTarget.closest('details')?.removeAttribute('open')}>How it works</a>
              <a href="#safety" onClick={(event) => event.currentTarget.closest('details')?.removeAttribute('open')}>Safety</a>
              <Link href={destination} onClick={(event) => event.currentTarget.closest('details')?.removeAttribute('open')}>{actionLabel}</Link>
            </div>
          </details>
        </div>
      </header>

      <section className="home-hero" aria-labelledby="home-title">
        <div className="home-hero-copy">
          <p className="eyebrow">Simple grocery help for everyday India</p>
          <h1 id="home-title">Say what you need. Stay in control.</h1>
          <p className="home-hero-lede">Speak or type your grocery list naturally. GANGU organizes it, explains the available choices, and always asks before anything happens.</p>
          <div className="hero-actions">
            <Link href={destination} className="primary-action"><Mic aria-hidden />{actionLabel}</Link>
            <a href="#sample" className="secondary-action">Try a safe sample <ArrowRight aria-hidden /></a>
          </div>
          <div className="language-line" aria-label="Supported languages"><Globe2 aria-hidden /><span><strong>हिन्दी</strong><i />English<i />Hinglish</span></div>
          <p className="hero-control-note"><ShieldCheck aria-hidden /> No purchase without your explicit confirmation.</p>
        </div>

        <div id="sample" className="product-story" aria-label="Safe example request">
          <div className="story-header"><div><span className="service-dot" /> Try a sample</div><span>No order placed</span></div>
          <div className="story-samples" role="group" aria-label="Choose a sample grocery request">
            {SAMPLE_REQUESTS.map((sample, index) => <button key={sample.label} type="button" aria-pressed={activeSample === index} onClick={() => setActiveSample(index)}>{sample.label}</button>)}
          </div>
          <div className="story-body" aria-live="polite">
            <div className="story-market-mark" aria-hidden><ShoppingBasket /><span>आज की सूची</span></div>
            <div className="sample-request"><Mic aria-hidden /><span><small>You say or type</small><strong>{SAMPLE_REQUESTS[activeSample].request}</strong></span></div>
            <div className="sample-result"><ListChecks aria-hidden /><span><small>GANGU understood</small><strong>{SAMPLE_REQUESTS[activeSample].result}</strong><p>{SAMPLE_REQUESTS[activeSample].detail}</p></span></div>
            <div className="sample-note"><Check aria-hidden />{SAMPLE_REQUESTS[activeSample].note}</div>
          </div>
          <p className="story-caption">This preview explains the workflow. It does not use live provider data or place an order.</p>
        </div>
      </section>

      <section className="home-principles" aria-label="GANGU product principles">
        <p>Made for real households</p>
        <div><strong>Voice first</strong><span>with a clear text alternative</span></div>
        <div><strong>Plain language</strong><span>instead of technical steps</span></div>
        <div><strong>Honest labels</strong><span>for live, estimated, and demo data</span></div>
      </section>

      <section id="features" className="home-section feature-section">
        <div className="section-kicker"><p className="eyebrow">Four things that matter</p><span>Clear capabilities, without feature overload</span></div>
        <div className="feature-heading"><h2>Less app to learn.<br />More useful help.</h2><p>Every part of GANGU supports one calm path: ask, understand, compare, and decide.</p></div>
        <div className="feature-showcase">
          <div className="feature-selector" role="group" aria-label="Explore GANGU capabilities">
            {FEATURES.map((feature, index) => {
              const Icon = feature.icon
              return <button key={feature.title} type="button" aria-pressed={activeFeature === index} aria-controls="feature-detail" className={`feature-choice feature-choice-${feature.tone}`} onClick={() => setActiveFeature(index)}><span><Icon aria-hidden /></span><strong>{feature.title}</strong><small>{String(index + 1).padStart(2, '0')}</small></button>
            })}
          </div>
          <div id="feature-detail" role="region" aria-live="polite" className={`feature-stage feature-stage-${FEATURES[activeFeature].tone}`}>
            <div className="feature-stage-top"><span>Capability {String(activeFeature + 1).padStart(2, '0')}</span><strong>{FEATURES[activeFeature].status}</strong></div>
            <div className="feature-stage-icon"><ActiveFeatureIcon aria-hidden /></div>
            <p className="feature-stage-label">{FEATURES[activeFeature].result}</p>
            <h3>{FEATURES[activeFeature].title}</h3>
            <p>{FEATURES[activeFeature].copy}</p>
            <div className="feature-example"><span>In practice</span><strong>{FEATURES[activeFeature].example}</strong></div>
            <div className="feature-stage-facts">{FEATURES[activeFeature].facts.map((fact) => <span key={fact}><Check aria-hidden />{fact}</span>)}</div>
          </div>
        </div>
        <div className="supporting-features" aria-label="More GANGU features">
          <span><ListChecks aria-hidden /><strong>Saved lists</strong> Browser-local and editable</span>
          <span><Eye aria-hidden /><strong>Comfort controls</strong> Larger text and contrast</span>
          <span><LockKeyhole aria-hidden /><strong>Secure sign-in</strong> Google and phone OTP</span>
          <span><BadgeCheck aria-hidden /><strong>Visible progress</strong> No mystery spinner</span>
        </div>
      </section>

      <section id="how" ref={howSectionRef} className="home-section how-section" onFocusCapture={() => setIsTracePlaying(false)}>
        <div className="how-intro">
          <p className="eyebrow">Follow one request</p>
          <h2>See how your words become a decision.</h2>
          <p>Watch one request move through GANGU automatically, or pause and select any step to inspect it at your own pace.</p>
          <div className="trace-playback">
            <button type="button" aria-pressed={isTracePlaying} onClick={() => setIsTracePlaying((playing) => !playing)}>
              {isTracePlaying ? <Pause aria-hidden /> : <Play aria-hidden />}
              {isTracePlaying ? 'Pause trace' : 'Play trace'}
            </button>
            <span><i className={isTracePlaying ? 'running' : ''} />{isTracePlaying ? 'Running automatically' : 'Paused for you'}</span>
          </div>
          <div id="request-trace-detail" className={`request-trace trace-stage-${HOW_STEPS[activeTrace].tone}`} role="region" aria-live={isTracePlaying ? 'off' : 'polite'} aria-atomic="true" aria-label={`Selected request stage: ${HOW_STEPS[activeTrace].traceTitle}`}>
            <div className="trace-auto-progress" aria-hidden><span key={activeTrace} className={isTracePlaying && isTraceVisible ? 'running' : ''} /></div>
            <div className="trace-route" aria-hidden>
              <span className="trace-route-fill" style={{ height: `${(activeTrace / (HOW_STEPS.length - 1)) * 100}%` }} />
              {HOW_STEPS.map((step, index) => {
                const Icon = step.icon
                return <span key={step.number} className={`trace-node trace-node-${step.tone} ${index === activeTrace ? 'active' : ''} ${index < activeTrace ? 'complete' : ''}`}><Icon /></span>
              })}
            </div>
            <div className="trace-output">
              <div className="trace-output-top"><span>Selected explanation</span><strong>{activeTrace + 1} / {HOW_STEPS.length}</strong></div>
              <div className="trace-icon"><ActiveTraceIcon aria-hidden /></div>
              <p>{HOW_STEPS[activeTrace].traceTitle}</p>
              <h3>{HOW_STEPS[activeTrace].traceCopy}</h3>
              <div className="trace-facts">{HOW_STEPS[activeTrace].facts.map((fact) => <span key={fact}><Check aria-hidden />{fact}</span>)}</div>
            </div>
            <p className="trace-caption">This is an explanation of the workflow, not a claim that live provider access is available.</p>
          </div>
        </div>
        <ol className="how-timeline">
          {HOW_STEPS.map((step, index) => (
            <li key={step.number} className={`timeline-${step.tone} ${activeTrace === index ? 'active' : ''}`}>
              <button type="button" aria-pressed={activeTrace === index} aria-controls="request-trace-detail" onClick={() => selectTrace(index)}>
                <span className="step-marker"><step.icon aria-hidden /><b>{step.number}</b></span><div><h3>{step.title}</h3><p>{step.copy}</p><small>{activeTrace === index ? 'Selected stage' : 'Select to inspect this stage'} <ArrowRight aria-hidden /></small>{activeTrace === index && <div className="mobile-trace-detail"><strong>{step.traceTitle}</strong><span>{step.traceCopy}</span></div>}</div>
              </button>
            </li>
          ))}
        </ol>
      </section>

      <section className="home-section access-section">
        <div className="access-visual">
          <p className="access-preview-label">Preview comfort controls</p>
          <div className="access-phone" aria-hidden>
            <span>GANGU</span><div className="access-mic"><Mic /></div><strong>Tap to speak</strong><small>or type your list below</small><div className="access-input">Atta, doodh, chai…</div>
          </div>
          <div className="comfort-controls" role="group" aria-label="Preview accessibility preferences">
            <button type="button" aria-pressed={settings.largerText} onClick={() => updateSettings({ largerText: !settings.largerText })}><strong>Aa</strong> Larger text</button>
            <button type="button" aria-pressed={settings.higherContrast} onClick={() => updateSettings({ higherContrast: !settings.higherContrast })}><Eye aria-hidden /> Higher contrast</button>
          </div>
          <p className="access-caption">These preferences are saved in this browser.</p>
        </div>
        <div className="access-copy">
          <p className="eyebrow">Comfort is a product feature</p><h2>Designed for older adults—and everyone helping at home.</h2><p>Large touch targets, visible focus, readable text, and adjustable contrast reduce effort without making the product feel clinical.</p>
          <ul>
            <li><Smartphone aria-hidden /><span><strong>Works across screen sizes</strong>Clear navigation from a small phone to a desktop.</span></li>
            <li><Eye aria-hidden /><span><strong>Preferences that reduce strain</strong>Larger text and higher contrast can be saved in this browser.</span></li>
            <li><Users aria-hidden /><span><strong>Household contacts, honestly described</strong>Contacts are browser-local today; no invitation or account permission is sent.</span></li>
          </ul>
        </div>
      </section>

      <section id="safety" className="home-section trust-section">
        <div className="trust-heading"><p className="eyebrow">Safety without vague promises</p><h2>Know what works now—and what still needs access.</h2></div>
        <div className="trust-ledger">
          <article><LockKeyhole aria-hidden /><div><h3>Verified sign-in</h3><p>Google and phone OTP use Firebase. Protected API requests require a valid Firebase ID token.</p></div><span>Available now</span></article>
          <article><BadgeCheck aria-hidden /><div><h3>Explicit final review</h3><p>The product, price, address, payment preference, and transaction mode are shown before confirmation.</p></div><span>Available now</span></article>
          <article><ListChecks aria-hidden /><div><h3>Saved household data</h3><p>Lists, contacts, and comfort preferences on these screens are currently saved in this browser.</p></div><span className="local">On this device</span></article>
          <article><ShoppingBasket aria-hidden /><div><h3>Swiggy provider connection</h3><p>Builders Club approval is received; Instamart MCP onboarding and credentials are in progress. Estimated data is labelled and cannot silently become a real order.</p></div><span className="pending">Onboarding</span></article>
        </div>
      </section>

      <section id="faq" className="home-section faq-section">
        <div className="faq-heading"><p className="eyebrow">Straight answers</p><h2>Before you begin</h2><p>What the current version can—and cannot—do.</p></div>
        <div className="faq-list">{FAQS.map(([question, answer]) => <details key={question}><summary><span>{question}</span><ChevronDown aria-hidden /></summary><p>{answer}</p></details>)}</div>
      </section>

      <section className="home-final-cta">
        <div><p className="eyebrow">Start with one sentence</p><h2>Grocery help should feel this simple.</h2><p>Sign in securely, speak or type your list, and review every important detail before confirming.</p></div>
        <Link href={destination} className="primary-action">{actionLabel}<ArrowRight aria-hidden /></Link>
      </section>

      <footer className="home-footer">
        <div><div className="brand-lockup"><Logo size={34} /><span><strong>GANGU</strong><small>grocery help · by voice</small></span></div><p>Built in India for calmer, clearer grocery decisions.</p></div>
        <nav aria-label="Footer navigation"><a href="#sample">Try a sample</a><a href="#features">Features</a><a href="#how">How it works</a><a href="#safety">Safety</a><a href="#faq">FAQ</a></nav>
        <p className="product-status">Current status: live provider purchasing remains disabled until verified access and safeguards are complete.</p>
      </footer>
    </main>
  )
}
