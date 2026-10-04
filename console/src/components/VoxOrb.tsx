import type { Material, BufferGeometry, MeshBasicMaterial } from "three";
import { useEffect, useRef, useState } from "react";
import { config } from "../services/api";
const colors: Record<string, string> = {
  IDLE: "#22d3ee",
  LISTENING: "#22d3ee",
  ANALYZING: "#8b5cff",
  HUMAN: "#25d07c",
  SYNTHETIC: "#ff4d6a",
  ABSTAIN: "#f6a935",
  UNKNOWN: "#22d3ee",
};
export default function VoxOrb({
  state = "IDLE",
  confidence = 72,
}: {
  state?: string;
  confidence?: number;
}) {
  const mount = useRef<HTMLDivElement>(null);
  const values = useRef({ state, confidence });
  values.current = { state, confidence };
  const [fallback, setFallback] = useState(!config.three);
  useEffect(() => {
    if (!config.three) return;
    let disposed = false,
      cleanup = () => {};
    void import("three")
      .then((T) => {
        if (disposed || !mount.current) return;
        try {
          const host = mount.current;
          const scene = new T.Scene();
          const camera = new T.PerspectiveCamera(35, 1, 0.1, 100);
          camera.position.z = 5.5;
          const renderer = new T.WebGLRenderer({
            alpha: true,
            antialias: true,
            powerPreference: "low-power",
          });
          renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
          host.appendChild(renderer.domElement);
          const group = new T.Group();
          scene.add(group);
          const materials: Material[] = [];
          const geometries: BufferGeometry[] = [];
          for (let i = 0; i < 3; i++) {
            const geo = new T.SphereGeometry(0.82 + i * 0.13, 32, 18);
            const mat = new T.MeshBasicMaterial({
              color: colors.IDLE,
              wireframe: true,
              transparent: true,
              opacity: 0.12 - i * 0.02,
            });
            geometries.push(geo);
            materials.push(mat);
            const shell = new T.Mesh(geo, mat);
            shell.rotation.z = i * 0.65;
            group.add(shell);
          }
          const pos = new Float32Array(450 * 3);
          for (let i = 0; i < 450; i++) {
            const theta = i * 2.399963,
              phi = Math.acos(1 - (2 * (i + 0.5)) / 450),
              r = 0.65 + (i % 7) * 0.075;
            pos.set(
              [
                r * Math.sin(phi) * Math.cos(theta),
                r * Math.sin(phi) * Math.sin(theta),
                r * Math.cos(phi),
              ],
              i * 3,
            );
          }
          const pg = new T.BufferGeometry();
          pg.setAttribute("position", new T.BufferAttribute(pos, 3));
          const pm = new T.PointsMaterial({
            color: colors.IDLE,
            size: 0.016,
            transparent: true,
            opacity: 0.8,
          });
          geometries.push(pg);
          materials.push(pm);
          group.add(new T.Points(pg, pm));
          for (let i = 0; i < 3; i++) {
            const geo = new T.TorusGeometry(1.25 + i * 0.09, 0.003, 4, 160);
            const mat = new T.MeshBasicMaterial({
              color: colors.IDLE,
              transparent: true,
              opacity: 0.6,
            });
            const ring = new T.Mesh(geo, mat);
            ring.rotation.set(Math.PI / 2 + 0.4 * i, 0.25 * i, 0.4);
            geometries.push(geo);
            materials.push(mat);
            group.add(ring);
          }
          const resize = () => {
            const w = host.clientWidth,
              h = host.clientHeight;
            renderer.setSize(w, h);
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
          };
          const observer = new ResizeObserver(resize);
          observer.observe(host);
          resize();
          const reduced = matchMedia("(prefers-reduced-motion: reduce)");
          let frame = 0;
          const animate = (time: number) => {
            frame = requestAnimationFrame(animate);
            if (document.hidden) return;
            const { state, confidence } = values.current;
            const color = new T.Color(colors[state] || colors.IDLE);
            materials.forEach((m) => {
              if ("color" in m)
                (m as MeshBasicMaterial).color.lerp(color, 0.045);
            });
            if (
              !reduced.matches &&
              config.motion &&
              !document.documentElement.classList.contains("reduce-motion")
            ) {
              group.rotation.y =
                time * (state === "ANALYZING" ? 0.00035 : 0.00007);
              group.rotation.z = Math.sin(time * 0.0002) * 0.08;
              group.scale.setScalar(
                1 + Math.sin(time * 0.001) * 0.015 * (confidence / 100),
              );
            }
            renderer.render(scene, camera);
          };
          animate(0);
          cleanup = () => {
            cancelAnimationFrame(frame);
            observer.disconnect();
            geometries.forEach((g) => g.dispose());
            materials.forEach((m) => m.dispose());
            renderer.dispose();
            renderer.domElement.remove();
          };
        } catch {
          setFallback(true);
        }
      })
      .catch(() => setFallback(true));
    return () => {
      disposed = true;
      cleanup();
    };
  }, []);
  return (
    <div
      className="orb-container"
      style={
        { "--orb-color": colors[state] || colors.IDLE } as React.CSSProperties
      }
    >
      <div ref={mount} className="orb-canvas" aria-hidden="true" />
      {fallback && (
        <div className="orb-fallback">
          <i />
          <i />
          <i />
          <i />
        </div>
      )}
      <span className="orb-coordinate top">09 EVIDENCE SYSTEMS / FUSION</span>
      <span className="orb-coordinate left">
        SIGNAL
        <br />
        FIELD
      </span>
      <span className="orb-coordinate right">
        {confidence.toFixed(1)}
        <br />
        CONFIDENCE
      </span>
      <div className="orb-state">
        <span className="status-dot" />
        {state === "IDLE" ? "SYSTEM OBSERVING" : state}
      </div>
    </div>
  );
}
