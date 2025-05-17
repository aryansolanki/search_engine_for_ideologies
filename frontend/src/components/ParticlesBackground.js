import React from 'react';
import Particles from 'react-tsparticles';
import { loadLinksPreset } from 'tsparticles-preset-links';

const ParticlesBackground = () => {
  const particlesInit = async (engine) => {
    await loadLinksPreset(engine);
  };

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={{
        preset: 'links',
        fullScreen: { enable: true, zIndex: -1 },
        background: {
          color: {
            value: "#f9f9f7"
          }
        },
        particles: {
          color: { value: "#444" },
          links: {
            color: "#aaa",
            distance: 130,
            enable: true,
            opacity: 0.3,
            width: 1
          },
          move: {
            enable: true,
            speed: 0.3
          },
          size: {
            value: { min: 1, max: 2 }
          },
          number: {
            value: 60,
            density: { enable: true, area: 800 }
          }
        }
      }}
    />
  );
};

export default ParticlesBackground;
