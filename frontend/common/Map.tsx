import { useEffect, useState, useRef } from "react";
import { Artist, Edge } from "@/api-codegen/client";
import dynamic from "next/dynamic";
import { graphUrlsEdges } from "@/api-codegen/client";
import { GraphData, LinkObject } from "react-force-graph-2d";
// Import dynamically because it uses canvas, which requires window
const ForceGraph = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

type MapProps = {
  artist?: Artist;
  onSelect: (artist: Artist) => void;
  onEdgeClick: (edge: Edge | undefined) => void;
};
export default function Map({ artist, onSelect, onEdgeClick }: MapProps) {
  const [graphData, setGraphData] = useState<GraphData<Artist> | undefined>();
  const graphRef = useRef<any>(undefined);
  const [focusedLink, setFocusedLink] = useState<LinkObject | undefined>();

  const [vinylImages, setVinylImages] = useState<Array<HTMLImageElement>>([]);
  useEffect(() => {
    const imgs = [
      "vinyl1.svg",
      "vinyl2.svg",
      "vinyl3.svg",
      "vinyl4.svg",
      "vinyl5.svg",
    ];
    setVinylImages(
      imgs.map((src) => {
        const img = new Image();
        img.src = `./${src}`;
        return img;
      })
    );
  }, []);

  useEffect(() => {
    async function fetchNeighbours() {
      if (!artist) return;

      const response = await graphUrlsEdges({
        query: { artist: artist.id },
      });
      const edges = response.data ?? [];

      function updateGraphData(prev: GraphData<Artist> | undefined) {
        if (!artist) return;

        const links = [];
        const nodes = [];

        // If the previous graph contains the current node, append previous nodes + links
        let joined = false;
        if (prev) {
          for (const node of prev.nodes) {
            if (node.id === artist.id) {
              nodes.push(...prev.nodes);
              links.push(...prev.links);
              joined = true;
              break;
            }
          }
        }
        if (!joined) {
          graphRef.current.zoom(5, 1000);
          graphRef.current.centerAt(0, 0, 1000);
        }

        // Add new links (bug - duplicate link)
        links.push(
          ...edges.map((edge) => ({
            source: edge.source.id,
            target: edge.target.id,
            sourceArtist: edge.source,
            targetArtist: edge.target,
          }))
        );

        // Add new nodes if they don't aready exist
        const nodeSet = new Set(nodes.map((node) => node.id));
        [artist, ...edges.map((edge) => edge.target)].forEach((artist) => {
          if (!nodeSet.has(artist.id)) {
            nodes.push(artist);
            nodeSet.add(artist.id);
          }
        });

        return { nodes: nodes, links: links };
      }
      setGraphData(updateGraphData);
    }
    fetchNeighbours();
  }, [artist]);

  // todo: can't seem to figure out how to type the ForceGraph component
  return (
    <ForceGraph
      graphData={graphData}
      nodeId="id"
      nodeLabel="name"
      maxZoom={10}
      linkColor={(link) => (link === focusedLink ? "gray" : "")}
      linkWidth={(link) => (link === focusedLink ? 2 : 1)}
      // linkDirectionalParticles={(link) => (link === focusedLink ? 3 : 0)}
      // linkDirectionalParticleWidth={2}
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.name;
        const fontSize = 12 / globalScale;
        ctx.font = `${fontSize}px Noto Serif`;
        const textWidth = ctx.measureText(label).width;
        const bckgDimensions = [textWidth, fontSize].map(
          (n) => n + fontSize * 0.2
        ); // some padding

        const imgSize = 6;
        ctx.drawImage(
          vinylImages[label.length % 5],
          (node.x ?? 0) - imgSize / 2,
          (node.y ?? 0) - imgSize / 2,
          imgSize,
          imgSize
        );

        ctx.fillStyle = "white";
        ctx.fillRect(
          (node.x ?? 0) - bckgDimensions[0] / 2,
          (node.y ?? 0) + imgSize / 2,
          bckgDimensions[0],
          bckgDimensions[1]
        );

        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = "black";
        ctx.fillText(
          label,
          node.x ?? 0,
          (node.y ?? 0) + imgSize / 2 + bckgDimensions[1] / 2
        );

        node.__imgSize = imgSize; // to re-use in nodePointerAreaPaint
      }}
      nodePointerAreaPaint={(node, color, ctx) => {
        ctx.fillStyle = color;
        const imgSize = node.__imgSize;
        ctx.fillRect(
          (node.x ?? 0) - imgSize / 2,
          (node.y ?? 0) - imgSize / 2,
          imgSize,
          imgSize
        );
      }}
      onNodeClick={(node) => {
        if (artist?.id === node.id) return;
        onSelect(node as Artist);
      }}
      ref={graphRef}
      onLinkClick={(link) => {
        if (link) {
          onEdgeClick({
            source: link.sourceArtist,
            target: link.targetArtist,
          });
          setFocusedLink(link);
        } else {
          setFocusedLink(undefined);
          onEdgeClick(undefined);
        }
      }}
    />
  );
}
