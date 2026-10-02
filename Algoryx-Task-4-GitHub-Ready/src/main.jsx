import React, { Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import { Canvas, useFrame } from '@react-three/fiber'
import { ContactShadows, Environment, OrbitControls, useGLTF } from '@react-three/drei'
import { ArrowRight, Download } from 'lucide-react'
import './styles.css'

function Mark({ dark = false }) {
  return <a className={`mark ${dark ? 'mark-dark' : ''}`} href="/index.html" aria-label="Submission home"><span className="mark-glyph">A</span><span>ALGORYX<br/><small>LAB SERIES</small></span></a>
}

function BeaconModel() {
  const {scene}=useGLTF('/assets/orbit-beacon.gltf')
  useFrame((state)=>{scene.rotation.y=state.clock.elapsedTime*.18})
  return <primitive object={scene} scale={1.2} position={[0,-.8,0]}/>
}

function Loader() { return <div className="model-loader"><span/><p>Loading 3D asset</p></div> }

function Creator() {
  return <div className="creator-site"><nav><Mark dark/><a href="/assets/orbit-beacon.gltf" download><Download/>Download GLTF</a></nav>
    <main className="creator-hero"><section><p className="eyebrow">ORIGINAL 3D ASSET · WEB READY</p><h1>Orbit<br/><em>Beacon</em></h1><p>A kinetic navigation monument built from a faceted energy core, three orbital bands, and a grounded signal pedestal.</p><div className="creator-tags"><span>GLTF 2.0</span><span>&lt; 1 MB</span><span>ORIGINAL</span></div></section><div className="beacon-stage"><Suspense fallback={<Loader/>}><Canvas camera={{position:[4,2.5,5],fov:42}}><ambientLight intensity={1.7}/><directionalLight position={[5,6,4]} intensity={3}/><pointLight position={[0,1,0]} intensity={15} color="#00d4ff"/><BeaconModel/><ContactShadows position={[0,-1.25,0]} opacity={.6} scale={8} blur={2.8}/><Environment preset="warehouse"/><OrbitControls enablePan={false}/></Canvas></Suspense><span>Drag to inspect</span></div></main>
    <section className="asset-story"><div><p className="eyebrow">DESIGN NOTES</p><h2>Signals made visible.</h2></div><p>Orbit Beacon is designed as a compact sci-fi prop for command centers, landing zones, and futuristic public spaces. Its silhouette remains legible at small sizes, while the intersecting rings create motion from every angle.</p></section>
    <section className="asset-data"><article><span>01</span><h3>Geometry</h3><p>Low-poly meshes with clean normals and efficient repeated forms.</p></article><article><span>02</span><h3>Materials</h3><p>Five PBR materials tuned for metal, ceramic, and emissive energy.</p></article><article><span>03</span><h3>Delivery</h3><p>Single self-contained GLTF with embedded binary data.</p></article></section>
    <section className="publish-card"><div><p>Suggested community listing</p><h2>Orbit Beacon</h2><p>A stylized sci-fi navigation beacon with an emissive core and orbital ring assembly. Designed for real-time WebGL scenes, games, and interactive product experiences.</p></div><div><span>Tags</span><p>sci-fi · prop · beacon · low-poly · webgl</p><span>Category</span><p>Props</p><span>License</span><p>Original work</p></div></section>
    <footer><Mark dark/><a href="/index.html">Back to submission hub <ArrowRight/></a></footer>
  </div>
}

createRoot(document.getElementById('root')).render(<React.StrictMode><Creator/></React.StrictMode>)
