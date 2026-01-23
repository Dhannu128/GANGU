# 🎨 GANGU Frontend - Visual Design Guide

## 🖼️ UI Mockup (Text-Based)

### Main Screen Layout

```
┌────────────────────────────────────────────────────────────────┐
│                         🛒 GANGU                               │
│                  Your Smart Grocery Assistant                  │
└────────────────────────────────────────────────────────────────┘
│                                                                │
│                                                                │
│                  What do you need today?                       │
│                                                                │
│                                                                │
│                      ╔═══════════════╗                         │
│                      ║               ║                         │
│                      ║      🎤       ║  ← Big Mic Button      │
│                      ║               ║    (Primary Input)     │
│                      ╚═══════════════╝                         │
│                                                                │
│                    Tap to speak                                │
│                                                                │
│                   ─── or type ───                             │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Type your message...                              📤 │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                │
│  [Order groceries] [Compare prices] [White chane le aao]      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Agent Timeline (While Processing)

```
┌────────────────────────────────────────────────────────────────┐
│  🤖 GANGU is thinking...                                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ✅ 🎯 Understanding your request                         │ │
│  │    "You want to buy white chickpeas"                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ✅ 🧠 Identifying item: White Chickpeas (1 kg)          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ⏳ 🔍 Searching platforms                               │ │
│  │    [Blinkit] [Amazon] [Flipkart]                        │ │
│  │    ⚪⚪⚪ Loading...                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### Product Comparison View

```
┌────────────────────────────────────────────────────────────────┐
│                  🛒 Here's what GANGU found                    │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐  ┌────────────┐
│ ✨ Recommended ✨   │  │                     │  │            │
│  by GANGU           │  │                     │  │            │
├─────────────────────┤  ├─────────────────────┤  ├────────────┤
│  BLINKIT            │  │  AMAZON             │  │  FLIPKART  │
│  [In Stock]         │  │  [In Stock]         │  │  [In Stock]│
│                     │  │                     │  │            │
│  ┌───────────────┐  │  │  ┌───────────────┐  │  │ ┌────────┐ │
│  │   [Product]   │  │  │  │   [Product]   │  │  │ │ [Prod] │ │
│  │   [Image]     │  │  │  │   [Image]     │  │  │ │ [Img]  │ │
│  └───────────────┘  │  │  └───────────────┘  │  │ └────────┘ │
│                     │  │                     │  │            │
│  White Chickpeas    │  │  White Chana        │  │  Kabuli    │
│  1 kg               │  │  1 kg               │  │  Chana 1kg │
│                     │  │                     │  │            │
│  ₹89                │  │  ₹104               │  │  ₹95       │
│  ⭐ 4.5            │  │  ⭐ 4.3            │  │  ⭐ 4.1   │
│  🚚 Today 6PM      │  │  🚚 Tomorrow       │  │  🚚 2 days │
│                     │  │                     │  │            │
│  💡 Best price +    │  │                     │  │            │
│  fastest delivery   │  │                     │  │            │
└─────────────────────┘  └─────────────────────┘  └────────────┘
        ↑ Click to select ↑
```

### Confirmation Modal

```
                    ╔══════════════════════════════╗
                    ║  🛒 Confirm Your Order       ║
                    ╠══════════════════════════════╣
                    ║                              ║
                    ║  Selected Product:           ║
                    ║  ┌────────────────────────┐  ║
                    ║  │ White Chickpeas (1kg)  │  ║
                    ║  │                        │  ║
                    ║  │ ₹89                    │  ║
                    ║  │                        │  ║
                    ║  │ Platform: Blinkit      │  ║
                    ║  │ Delivery: Today 6 PM   │  ║
                    ║  └────────────────────────┘  ║
                    ║                              ║
                    ║  💡 Why GANGU recommends:    ║
                    ║  "Best price + fastest       ║
                    ║   delivery available"        ║
                    ║                              ║
                    ║  I'll place this order on    ║
                    ║  Blinkit. Should I proceed?  ║
                    ║                              ║
                    ║  ┌──────────────────────┐    ║
                    ║  │ ✅ Confirm Purchase  │    ║
                    ║  └──────────────────────┘    ║
                    ║                              ║
                    ║  ┌──────────────────────┐    ║
                    ║  │ 🔁 Change Option     │    ║
                    ║  └──────────────────────┘    ║
                    ║                              ║
                    ║  ❌ Cancel                   ║
                    ║                              ║
                    ╚══════════════════════════════╝
```

### Success Screen

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║                          ┌─────────┐                          ║
║                          │    ✓    │                          ║
║                          │         │                          ║
║                          └─────────┘                          ║
║                                                                ║
║                     🎉 Order Placed!                          ║
║                                                                ║
║                Your order has been confirmed                  ║
║                                                                ║
║  ┌──────────────────────────────────────────────────────┐     ║
║  │  Order ID:    ORD-1234567890                        │     ║
║  │                                                      │     ║
║  │  Product:     White Chickpeas (1 kg)                │     ║
║  │                                                      │     ║
║  │  Platform:    Blinkit                               │     ║
║  │                                                      │     ║
║  │  Price:       ₹89                                   │     ║
║  │                                                      │     ║
║  │  ─────────────────────────────────────────────       │     ║
║  │                                                      │     ║
║  │  🕐 Delivery: Today by 6:00 PM                      │     ║
║  └──────────────────────────────────────────────────────┘     ║
║                                                                ║
║  ┌────────────────────────────────────────────────────┐       ║
║  │        Order Something Else                        │       ║
║  └────────────────────────────────────────────────────┘       ║
║                                                                ║
║  ┌────────────────────────────────────────────────────┐       ║
║  │        📦 Track Order                              │       ║
║  └────────────────────────────────────────────────────┘       ║
║                                                                ║
║             Thank you for using GANGU! 🙏                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

## 🎨 Color Palette

```
Primary Green:   #10B981  ████  Calm, trustworthy
Secondary Blue:  #3B82F6  ████  Professional
Accent Amber:    #F59E0B  ████  Warm, attention
Dark Text:       #1F2937  ████  High contrast
Light BG:        #F9FAFB  ████  Soft background
Success:         #10B981  ████  Positive feedback
Error:           #EF4444  ████  Errors/cancel
Warning:         #F59E0B  ████  Caution
```

## 📱 Mobile Layout (< 640px)

```
┌──────────────────────┐
│    🛒 GANGU         │
│  Grocery Assistant   │
├──────────────────────┤
│                      │
│   What do you need?  │
│                      │
│     ╔═══════╗        │
│     ║  🎤  ║        │ ← Larger on mobile
│     ╚═══════╝        │
│                      │
│    Tap to speak      │
│                      │
│   ─── or type ───   │
│                      │
│  ┌────────────────┐  │
│  │ Type... 📤    │  │
│  └────────────────┘  │
│                      │
│  [Quick suggestions] │
│                      │
├──────────────────────┤
│  Agent Timeline      │
│  (Scrollable)        │
├──────────────────────┤
│  Product Cards       │
│  (Single column)     │
│                      │
│  ┌────────────────┐  │
│  │ [Product 1]    │  │
│  │ Full width     │  │
│  └────────────────┘  │
│                      │
│  ┌────────────────┐  │
│  │ [Product 2]    │  │
│  └────────────────┘  │
│                      │
└──────────────────────┘
```

## 🖱️ Interaction States

### Mic Button States

```
Normal:      ⭕ Gray circle with mic icon
Hover:       ⭕ Scales to 110%, shadow grows
Active:      🔴 Red, pulsing animation
Recording:   🔴 Red with waveform animation
Processing:  ⚪ Gray with spinner
```

### Product Card States

```
Normal:       White background, subtle shadow
Hover:        Shadow grows, slight scale
Recommended:  Green ring, green border
Selected:     Blue border, blue highlight
Clicked:      Brief scale animation
```

### Button States

```
Primary:      Green bg, white text
Hover:        Darker green, shadow
Active:       Even darker, scale 95%
Disabled:     Gray, no hover, cursor not-allowed
Loading:      Spinner inside button
```

## ✨ Animations

### Fade In
```
Elements fade in from bottom:
  0% → opacity: 0, translateY: 10px
100% → opacity: 1, translateY: 0px
Duration: 300ms
```

### Pulse (Listening)
```
Mic button pulses when active:
  0% → scale: 1, opacity: 1
 50% → scale: 1.05, opacity: 0.8
100% → scale: 1, opacity: 1
Duration: 2s, infinite
```

### Checkmark (Complete)
```
Timeline step completion:
- Green background fades in
- Checkmark icon appears
- Subtle slide from left
Duration: 200ms
```

### Loading Dots
```
Three dots bounce:
Dot 1: delay 0s
Dot 2: delay 0.2s
Dot 3: delay 0.4s
```

## 🔤 Typography

```
Headings:
  H1: 2.5rem (40px), bold
  H2: 2rem (32px), bold
  H3: 1.5rem (24px), semibold

Body:
  Large: 1.125rem (18px), normal
  Normal: 1rem (16px), normal
  Small: 0.875rem (14px), normal

Font Family:
  Inter (Google Font)
  Fallback: system-ui, sans-serif
```

## 📐 Spacing

```
Gap/Padding Scale:
  xs:  0.25rem (4px)
  sm:  0.5rem (8px)
  md:  1rem (16px)
  lg:  1.5rem (24px)
  xl:  2rem (32px)
  2xl: 3rem (48px)

Border Radius:
  sm:  0.25rem (4px)
  md:  0.5rem (8px)
  lg:  1rem (16px)
  full: 9999px (circle)
```

## 🎭 Accessibility

```
✅ Large tap targets (44x44px minimum)
✅ High contrast text (4.5:1 minimum)
✅ Focus indicators on all interactive elements
✅ Screen reader labels (aria-label)
✅ Keyboard navigation support
✅ Reduced motion support (prefers-reduced-motion)
```

## 🌈 Visual Hierarchy

```
Most Important (Draw attention):
  - Mic button (large, centered)
  - Recommended product (green ring)
  - Confirm button (large, green)

Important:
  - Product prices (large, bold)
  - Agent timeline (colored borders)
  - Success message (large checkmark)

Supporting:
  - Product details (normal size)
  - Suggestions (small chips)
  - Footer text (small, gray)
```

## 📊 Layout Grid

```
Desktop (> 1024px):
  - 3 column product grid
  - Max width: 1280px
  - Padding: 32px

Tablet (640-1024px):
  - 2 column product grid
  - Max width: 100%
  - Padding: 24px

Mobile (< 640px):
  - 1 column
  - Max width: 100%
  - Padding: 16px
```

---

**This visual guide ensures GANGU looks consistent, professional, and trustworthy! 🎨**
