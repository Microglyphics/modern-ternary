import React, { useState } from 'react';

// TernaryPlot Component
const TernaryPlot = ({ analysisData }) => {
    const [layers, setLayers] = useState({
        baseline: true,
        gridLines: true,
        mixTriangle: true,
        shading: true
    });

    const width = 800;
    const height = 700;
    const margin = { top: 50, right: 50, bottom: 50, left: 50 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;

    // Calculate triangle vertices
    const vertices = {
        top: { x: plotWidth / 2 + margin.left, y: margin.top }, // Modern
        left: { x: margin.left, y: height - margin.bottom }, // PostModern
        right: { x: width - margin.right, y: height - margin.bottom } // PreModern
    };

    // Convert ternary coordinates to Cartesian
    const ternaryToCartesian = (pre, mod, post) => {
        const total = pre + mod + post;
        const normalizedPre = pre / total;
        const normalizedMod = mod / total;
        const normalizedPost = post / total;

        const x = vertices.left.x * normalizedPost + 
                 vertices.top.x * normalizedMod + 
                 vertices.right.x * normalizedPre;

        const y = vertices.left.y * normalizedPost + 
                 vertices.top.y * normalizedMod + 
                 vertices.right.y * normalizedPre;

        return { x, y };
    };

    // Calculate plot point position
    const plotPoint = ternaryToCartesian(...analysisData.scores);

    return (
        <div className="relative">
            <LayerControls layers={layers} setLayers={setLayers} />
            <svg 
                width={width} 
                height={height} 
                className="bg-white mx-auto"
                viewBox={`0 0 ${width} ${height}`}
            >
                {/* Base triangle */}
                {layers.baseline && (
                    <path
                        d={`M ${vertices.left.x} ${vertices.left.y} 
                           L ${vertices.top.x} ${vertices.top.y} 
                           L ${vertices.right.x} ${vertices.right.y} 
                           Z`}
                        stroke="black"
                        strokeWidth="2"
                        fill="none"
                    />
                )}
                
                {/* Plot point */}
                <circle
                    cx={plotPoint.x}
                    cy={plotPoint.y}
                    r="6"
                    fill="red"
                    stroke="white"
                    strokeWidth="2"
                />
            </svg>
        </div>
    );
};

export default TernaryPlot;