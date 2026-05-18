---
name: Cali Tourism Design System
colors:
  surface: '#fff8f3'
  surface-dim: '#e5d8c8'
  surface-bright: '#fff8f3'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff2e2'
  surface-container: '#faecdb'
  surface-container-high: '#f4e6d6'
  surface-container-highest: '#eee0d0'
  on-surface: '#211b11'
  on-surface-variant: '#514532'
  inverse-surface: '#372f24'
  inverse-on-surface: '#fdefde'
  outline: '#847560'
  outline-variant: '#d6c4ac'
  surface-tint: '#7e5700'
  primary: '#7e5700'
  on-primary: '#ffffff'
  primary-container: '#ffb300'
  on-primary-container: '#6b4900'
  inverse-primary: '#ffba38'
  secondary: '#bb0020'
  on-secondary: '#ffffff'
  secondary-container: '#e12634'
  on-secondary-container: '#fffbff'
  tertiary: '#2c694e'
  on-tertiary: '#ffffff'
  tertiary-container: '#90cfae'
  on-tertiary-container: '#1a5a40'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdeac'
  primary-fixed-dim: '#ffba38'
  on-primary-fixed: '#281900'
  on-primary-fixed-variant: '#604100'
  secondary-fixed: '#ffdad7'
  secondary-fixed-dim: '#ffb3af'
  on-secondary-fixed: '#410005'
  on-secondary-fixed-variant: '#930017'
  tertiary-fixed: '#b1f0ce'
  tertiary-fixed-dim: '#95d4b3'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#0e5138'
  background: '#fff8f3'
  on-background: '#211b11'
  surface-variant: '#eee0d0'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '800'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 30px
  body-lg:
    fontFamily: Be Vietnam Pro
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Be Vietnam Pro
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-lg:
    fontFamily: Be Vietnam Pro
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Be Vietnam Pro
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 20px
  lg: 32px
  xl: 48px
  gutter: 16px
  margin: 20px
---

## Brand & Style

The design system is a celebration of the "Sucursal del Cielo," designed to evoke the rhythmic energy of Cali while maintaining a high-performance, functional interface. It targets a diverse audience of local and international travelers seeking authentic cultural immersion, from salsa clubs to mountain hikes. 

The visual style is **Vibrant Modernism**. It blends the cleanliness of modern digital interfaces with the soul of Caleño folk art. It utilizes high-contrast color pairings and rhythmic patterns inspired by the *macetas* (sugar figurines) given on the Day of Godchildren. The interface remains lightweight and accessible, using whitespace strategically to let the bold photography and colorful accents breathe. The goal is to feel as welcoming and energetic as a warm afternoon in San Antonio.

## Colors

The palette is a direct reflection of Cali's landscape and heritage. 
- **Sunshine Yellow** (Primary) acts as the foundation of the brand, bringing warmth and optimism. It is used for primary backgrounds and high-level brand moments.
- **Salsa Red** (Secondary) is the pulse of the app, reserved for high-energy interactions, key call-to-actions, and notifications.
- **Farallones Green** (Tertiary) provides a lush, grounded contrast, representing the surrounding mountains and used for environmental and nature-focused content.
- **Deep Sky Blue** is used for functional interactive elements, links, and travel-specific information like flight or weather statuses.

The base background is a warm off-white (Cream) to reduce glare under the bright Colombian sun while maintaining better readability than pure white.

## Typography

This design system utilizes a dual-font strategy to balance personality with legibility. 

**Plus Jakarta Sans** is the headline face. Its soft, rounded terminals and optimistic character make it perfect for titles and hero sections, capturing the "friendly" nature of the brand. It should be used in Bold or Extra Bold weights to create a strong visual hierarchy.

**Be Vietnam Pro** is the workhorse for body text and labels. It offers a contemporary, clean look with exceptional legibility at small sizes. Its slightly wider apertures ensure that even dense travel information remains accessible and easy to scan while on the move.

## Layout & Spacing

The system employs a **fluid grid** model designed for mobile-first consumption. 
- A standard 4-column grid is used for mobile devices with 20px side margins to prevent content from touching the screen edges.
- Spacing follows a rhythmic 8px base unit, but introduces "odd" steps (like 12px and 20px) to prevent the layout from feeling too rigid or corporate. 
- Horizontal scrolling "shelves" are used frequently for discovery-based content (e.g., "Nearby Salsa Schools") to maximize vertical screen real estate while maintaining a sense of abundance.

## Elevation & Depth

Depth in this design system is created through **Tonal Layers** and **Tinted Shadows**. 
- Surfaces do not use generic gray shadows; instead, they use soft, diffused shadows tinted with a hint of Salsa Red or Sky Blue to maintain the "vibrant" feel even in the shadows.
- Cards and modal elements use a subtle 1px inner stroke in a lighter version of the primary color to create a "lifting" effect from the warm background.
- Background patterns inspired by *macetas* (zig-zags and floral starbursts) are placed on the lowest layer, often with a slight backdrop blur to ensure that foreground content remains the focal point while the culture stays visible.

## Shapes

The shape language is consistently **Rounded**, avoiding sharp corners to mirror the welcoming and fluid nature of Cali's culture. 
- Standard UI components (buttons, input fields) use a 0.5rem (8px) corner radius.
- Large containers and immersive cards use a 1.5rem (24px) radius to create a soft, friendly framing for photography.
- Select decorative elements, such as "Deal" tags or category chips, may utilize pill-shaped (fully rounded) geometry to differentiate them from functional inputs.

## Components

- **Buttons**: Primary buttons are solid Salsa Red with white text. Secondary buttons use a Sky Blue outline. All buttons feature a subtle rhythmic bounce animation on press.
- **Chips**: Used for filtering (e.g., "Live Music," "Nature," "Gastronomy"). Active chips take on the Farallones Green background with white text to signify a "selected" state.
- **Cards**: Travel cards feature high-quality edge-to-edge imagery at the top. The footer of the card uses a subtle pattern-fill background (inspired by local alfeñique paper textures) in a low-opacity sunshine yellow.
- **Input Fields**: Modern, bottom-line only or lightly filled containers. Focus states use a thick 2px Sunshine Yellow border.
- **Icons**: Icons are stroke-based with a medium weight (2px). They should feature occasional "disconnected" paths or expressive flourishes to feel hand-drawn yet modern.
- **Macetas Pattern**: A decorative component used as a header background or section divider. It consists of geometric starbursts and streamers in the four brand colors.
- **Rhythm Progress Bar**: A custom loading component that mimics the beat of a Clave, adding a small cultural Easter egg to the functional wait times.