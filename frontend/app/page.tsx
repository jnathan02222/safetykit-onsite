"use client";
import { useEffect, useState } from "react";
import {
  graphUrlsListPolicies,
  type PolicyViolationOut,
} from "../api-codegen/client";

export default function Home() {
  const [policies, setPolicies] = useState<PolicyViolationOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showOnlyViolations, setShowOnlyViolations] = useState(false);
  const [showOnlyAdderall, setShowOnlyAdderall] = useState(false);
  const [expandedPolicies, setExpandedPolicies] = useState<Set<number>>(
    new Set(),
  );

  useEffect(() => {
    async function fetchPolicies() {
      try {
        const response = await graphUrlsListPolicies();
        setPolicies(response.data ?? []);
      } catch (error) {
        console.error("Failed to fetch policies:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchPolicies();
  }, []);

  const togglePolicy = (id: number) => {
    setExpandedPolicies((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  // Filter policies based on toggles
  let filteredPolicies = policies;

  if (showOnlyAdderall) {
    filteredPolicies = filteredPolicies.filter((p) => p.is_adderall_sold);
  }

  if (showOnlyViolations) {
    filteredPolicies = filteredPolicies.filter(
      (p) => p.is_adderall_sold && p.uses_visa && !p.appears_licensed_pharmacy,
    );
  }

  if (loading) {
    return <div className="p-8">Loading policies...</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Policy Violations</h1>

        <div className="flex items-center gap-6">
          <label className="flex items-center gap-3 cursor-pointer">
            <span className="text-sm font-medium text-gray-700">
              Show only Adderall
            </span>
            <div className="relative">
              <input
                type="checkbox"
                checked={showOnlyAdderall}
                onChange={(e) => setShowOnlyAdderall(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-600"></div>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <span className="text-sm font-medium text-gray-700">
              Show only violations
            </span>
            <div className="relative">
              <input
                type="checkbox"
                checked={showOnlyViolations}
                onChange={(e) => setShowOnlyViolations(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
            </div>
          </label>

          <span className="text-xs text-gray-500">
            ({filteredPolicies.length} of {policies.length})
          </span>
        </div>
      </div>

      {filteredPolicies.length === 0 ? (
        <p className="text-gray-500">
          {showOnlyViolations
            ? "No violations found (Adderall sold + Visa accepted + Not licensed)."
            : showOnlyAdderall
              ? "No sites found selling Adderall."
              : "No policy violations found."}
        </p>
      ) : (
        <div className="space-y-4">
          {filteredPolicies.map((policy) => {
            const isExpanded = expandedPolicies.has(policy.id);
            return (
              <div
                key={policy.id}
                className="border rounded-lg shadow-sm bg-white overflow-hidden"
              >
                {/* Collapsible Header */}
                <button
                  onClick={() => togglePolicy(policy.id)}
                  className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-lg font-semibold truncate">
                        {policy.title}
                      </h2>
                      {/* Status badges inline */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {policy.is_adderall_sold && (
                          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Adderall
                          </span>
                        )}
                        {policy.uses_visa && (
                          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Visa
                          </span>
                        )}
                        {!policy.appears_licensed_pharmacy && (
                          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            Unlicensed
                          </span>
                        )}
                      </div>
                    </div>
                    <a
                      href={policy.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm truncate block"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {policy.url}
                    </a>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                    <span className="text-sm text-gray-500">
                      {new Date(policy.analyzed_at).toLocaleDateString()}
                    </span>
                    <svg
                      className={`w-5 h-5 text-gray-500 transition-transform ${
                        isExpanded ? "rotate-180" : ""
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </div>
                </button>

                {/* Expandable Content */}
                {isExpanded && (
                  <div className="p-6 pt-0 border-t">
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Adderall Sold:</span>
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            policy.is_adderall_sold
                              ? "bg-red-100 text-red-800"
                              : "bg-green-100 text-green-800"
                          }`}
                        >
                          {policy.is_adderall_sold ? "Yes" : "No"}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="font-medium">Licensed Pharmacy:</span>
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            policy.appears_licensed_pharmacy
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {policy.appears_licensed_pharmacy ? "Yes" : "No"}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="font-medium">Uses Visa:</span>
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            policy.uses_visa
                              ? "bg-blue-100 text-blue-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {policy.uses_visa ? "Yes" : "No"}
                        </span>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-4 rounded mb-4">
                      <p className="font-medium mb-2">Analysis:</p>
                      <p className="text-gray-700">{policy.explanation}</p>
                    </div>

                    {policy.screenshots && policy.screenshots.length > 0 && (
                      <div>
                        <p className="font-medium mb-3">
                          Screenshots ({policy.screenshots.length}):
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {policy.screenshots.map((screenshot, index) => (
                            <div
                              key={index}
                              className="border rounded overflow-hidden"
                            >
                              <img
                                src={`data:image/png;base64,${screenshot}`}
                                alt={`Screenshot ${index + 1}`}
                                className="w-full h-auto"
                              />
                              <div className="bg-gray-100 px-3 py-2 text-sm text-gray-600">
                                Screenshot {index + 1}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
