import { graphUrlsEdgeDescription } from "@/api-codegen/client";
import { useCallback, useEffect, useRef, useState } from "react";
import { debounce } from "@tanstack/react-pacer";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import { Edge } from "@/api-codegen/client";

export default function EdgeSidebar({ edge }: { edge: Edge | undefined }) {
  const [edgeDescription, setEdgeDescription] = useState<
    string | undefined | null
  >();
  const latestTimestamp = useRef(0);
  const [isLoading, setIsLoading] = useState(false);

  //
  // todo: use a library for this (TanStack?)
  function setResultsLatest(result: string | undefined, timestamp: number) {
    if (timestamp >= latestTimestamp.current) {
      latestTimestamp.current = timestamp;
      setEdgeDescription(result);
    }
  }

  const getEdgeDescription = useCallback(
    debounce(
      async (edge: Edge | undefined) => {
        const timestamp = Date.now();
        setResultsLatest(undefined, timestamp);
        setIsLoading(true);
        if (!edge) {
          return;
        }
        const response = await graphUrlsEdgeDescription({
          query: { source: edge.source.id, target: edge.target.id },
        });
        setIsLoading(false);

        let description = "";
        if (response.data) {
          for (const item of response.data) {
            description += `<b>${item.source.name} → ${item.target.name}</b>`;
            description += item.wikipedia_description + "<br>";
          }
        }
        setResultsLatest(description, timestamp);
      },
      { wait: 100 }
    ),
    []
  );

  useEffect(() => {
    getEdgeDescription(edge);
  }, [edge]);
  return (
    <>
      {edge && (
        <div className="absolute w-128 max- w-128 right-0 h-screen max-h-screen p-12 z-10 bg-white opacity-90 overflow-y-scroll overflow-x-hidden">
          {isLoading && (
            <div className="w-full">
              <Skeleton count={5} />
            </div>
          )}

          <div
            dangerouslySetInnerHTML={{ __html: edgeDescription ?? "" }}
          ></div>
        </div>
      )}
    </>
  );
}
