---
name: web-3d
description: Add 3D and WebGL to websites — interactive hero objects, product viewers, particles, shader backgrounds, scroll-driven 3D scenes — with Three.js or React Three Fiber (drei), Spline, or model-viewer, while keeping load time, mobile performance and fallbacks under control. Use whenever the user mentions 3D, WebGL, Three.js, R3F, react-three-fiber, shaders, GLB/GLTF models, particles, Spline, or wants an immersive/"wow" hero.
---

# Web 3D

3D is the heaviest thing on a page. Treat it as a progressive enhancement layered on a page that already works and looks good without it.

## 1. Pick the right tool
| Need | Use |
|---|---|
| Show a product model, rotate/zoom, AR | `<model-viewer>` web component — simplest, accessible |
| Designer built the scene visually | Spline (export as React component / embed) — fast to ship, heavier runtime |
| Custom interactive scene in React/Next.js | React Three Fiber: `npm i three @react-three/fiber @react-three/drei` |
| Custom scene in vanilla / Vue / Astro | Three.js directly (`npm i three`) — or TresJS for Vue |
| Gradient/noise background, distortion effects | A single fullscreen shader plane (Three.js) or a lighter lib like OGL |

## 2. Assets
- Models: GLB, compressed. `npx gltf-transform optimize in.glb out.glb --texture-compress webp` (Draco/Meshopt geometry + compressed textures). Target < 2–3 MB for a hero, ideally < 1 MB.
- Textures: power-of-two sizes, ≤ 2048px, WebP/KTX2.
- Generate typed R3F components from models: `npx gltfjsx model.glb --transform`.
- Bake lighting into textures when possible instead of many real-time lights/shadows.

## 3. Loading strategy (protect LCP)
- The hero's text and CTA render as normal HTML first. The canvas loads after, behind them or beside them.
- Next.js: `const Scene = dynamic(() => import("./Scene"), { ssr: false })`. Load when near viewport (IntersectionObserver) if not above the fold.
- Show a poster image (a render of the scene) until the canvas is ready, then crossfade — no layout shift (fixed aspect-ratio container).
- drei `<Preload all />`, `useGLTF.preload(url)`; `<Suspense fallback={…}>`.

## 4. R3F essentials
```tsx
<Canvas dpr={[1, 1.75]} camera={{ position: [0, 0, 5], fov: 45 }}
  gl={{ antialias: true, powerPreference: "high-performance" }}>
  <Suspense fallback={null}>
    <Environment preset="city" />
    <Model />
  </Suspense>
</Canvas>
```
- Animate in `useFrame((state, delta) => { ref.current.rotation.y += delta * 0.3 })` — mutate refs, never `setState` per frame.
- Pointer interaction: use `state.pointer` inside `useFrame` and lerp toward it (`THREE.MathUtils.damp`) for smooth follow.
- Scroll-linked 3D: drei `ScrollControls` + `useScroll`, or read GSAP ScrollTrigger progress into a ref that `useFrame` reads.
- Reuse geometries/materials; use `<Instances>`/`InstancedMesh` for many copies (particles, grids).
- `frameloop="demand"` for mostly-static scenes (render only on change) — big battery win.
- Pause rendering when the canvas is off-screen.

## 5. Performance & mobile
- Cap DPR (`dpr={[1, 1.5]}` on mobile). Fewer lights, no or baked shadows, lower particle counts on mobile.
- drei `<PerformanceMonitor>` / `AdaptiveDpr` to degrade quality automatically.
- Budget: < 100 draw calls for a hero, steady 60fps on a mid-range phone. Check with `r3f-perf` in development.
- Dispose of geometries/textures/materials on unmount in vanilla Three.js (R3F does this automatically for its own objects).

## 6. Accessibility & fallbacks
- Canvas is decorative → `aria-hidden="true"`; all meaningful content stays in HTML.
- Interactive viewer → keyboard controls or buttons for rotate/zoom, plus a text description.
- Reduced motion → stop auto-rotation and idle animations (static frame).
- No WebGL / low-power device → keep the poster image. Detect failure with an error boundary around `<Canvas>`.
- Don't hijack scroll or wheel on the canvas unless the scene is the whole experience.

## 7. Verify
Check network weight of the 3D assets, Lighthouse LCP with and without the scene, fps on throttled CPU, mobile at 375px, reduced motion, and WebGL-disabled fallback.
