"use client";
import { useRef, useState } from "react";
import SearchBar from "@/common/SearchBar";
import Map from "@/common/Map";
import EdgeSidebar from "@/common/EdgeSidebar";
import { Artist, Edge, graphUrlsSearch } from "@/api-codegen/client";

export default function Home() {
  const [selectedArtist, setSelectedArtist] = useState<Artist | undefined>();
  const [searchValue, setSearchValue] = useState("");
  const [results, setResults] = useState<Artist[]>([]);
  const latestTimestamp = useRef(0);

  const [showDescription, setShowDescription] = useState(false);
  const [selectedEdge, setSelectedEdge] = useState<Edge | undefined>();

  function setResultsLatest(results: Artist[], timestamp: number) {
    if (timestamp > latestTimestamp.current) {
      latestTimestamp.current = timestamp;
      setResults(results);
    }
  }
  function onSelect(artist: Artist) {
    setSearchValue(artist.name);
    setResultsLatest([], Date.now());
    setSelectedArtist(artist);
    setShowDescription(true);
  }

  async function handleSearch(value: string) {
    const timestamp = Date.now();
    setShowDescription(false);

    setSearchValue(value);
    if (value == "") {
      setResultsLatest([], timestamp);
      return;
    }
    // TODO: debounce?
    const response = await graphUrlsSearch({ query: { name: value } });
    setResultsLatest(response.data ?? [], timestamp);
  }

  return (
    <div>
      <div className="p-12 absolute z-10">
        <SearchBar
          placeholder="Enter a musician"
          onSelect={onSelect}
          handleSearch={handleSearch}
          searchValue={searchValue}
          results={results}
        />
        {showDescription && (
          <>
            <div className="text-gray-500">
              {selectedArtist?.wikipedia_description}
            </div>
          </>
        )}
      </div>
      <EdgeSidebar edge={selectedEdge}></EdgeSidebar>
      <Map
        artist={selectedArtist}
        onSelect={onSelect}
        onEdgeClick={(edge: Edge | undefined) => {
          setSelectedEdge(edge);
        }}
      />
    </div>
  );
}
