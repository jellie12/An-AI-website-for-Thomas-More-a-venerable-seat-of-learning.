"use client";

import { useState, useRef } from "react";
import {
  Upload,
  Leaf,
  AlertTriangle,
  Shield,
  TrendingDown,
  TrendingUp,
  Minus,
  Info,
  Target,
  Heart,
  Globe,
  TreePine,
  Camera,
} from "lucide-react";

interface AnimalAnalysis {
  animal_name: string | null;
  scientific_name: string | null;
  conservation_status: string | null;
  population_trend: string | null;
  estimated_population: string | null;
  habitat: string | null;
  background: string | null;
  threats: string | null;
  sdg_connection: string | null;
  conservation_efforts: string | null;
  not_animal: boolean;
  message: string | null;
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnimalAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("background");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysis(null);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysis(null);
      setError(null);
    }
  };

 const analyzeImage = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      const text = await response.text();
      
      if (!response.ok) {
        let errorMessage = "Failed to analyze image";
        try {
          const errJson = JSON.parse(text);
          errorMessage = errJson.detail || errorMessage;
        } catch {
          errorMessage = text || errorMessage;
        }
        throw new Error(errorMessage);
      }

      let data: AnimalAnalysis;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error("Invalid response from server");
      }
      
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getStatusStyle = (status: string | null) => {
    if (!status) return "bg-muted text-muted-foreground";
    const lower = status.toLowerCase();
    if (lower.includes("critically") || lower.includes("endangered")) {
      return "bg-endangered text-white";
    }
    if (lower.includes("vulnerable") || lower.includes("near threatened")) {
      return "bg-vulnerable text-white";
    }
    return "bg-safe text-white";
  };

  const getTrendIcon = (trend: string | null) => {
    if (!trend) return <Minus className="w-4 h-4" />;
    const lower = trend.toLowerCase();
    if (lower.includes("decreasing")) return <TrendingDown className="w-4 h-4 text-endangered" />;
    if (lower.includes("increasing")) return <TrendingUp className="w-4 h-4 text-safe" />;
    return <Minus className="w-4 h-4 text-muted-foreground" />;
  };

  const tabs = [
    { id: "background", label: "Background", icon: Info },
    { id: "habitat", label: "Habitat & Threats", icon: TreePine },
    { id: "sdg", label: "SDG 15", icon: Globe },
    { id: "conservation", label: "Conservation", icon: Heart },
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-primary text-primary-foreground">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="flex items-center gap-3 mb-2">
            <Leaf className="w-8 h-8" />
            <h1 className="text-3xl font-bold">Wildlife Scanner</h1>
          </div>
          <p className="text-primary-foreground/90 text-lg">
            Identify animals and learn about their conservation status
          </p>
          <div className="mt-4 inline-flex items-center gap-2 bg-safe px-4 py-2 rounded-full text-sm font-medium">
            <Target className="w-4 h-4" />
            SDG 15: Life on Land
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div>
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Camera className="w-5 h-5 text-primary" />
              Upload an Animal Image
            </h2>

            <div
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="border-2 border-dashed border-primary/30 rounded-2xl p-8 text-center cursor-pointer hover:border-primary/60 hover:bg-secondary/50 transition-all"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />

              {previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-h-64 mx-auto rounded-xl object-contain"
                />
              ) : (
                <div className="py-8">
                  <Upload className="w-12 h-12 mx-auto text-primary/50 mb-4" />
                  <p className="text-foreground font-medium mb-2">
                    Drop an image here or click to browse
                  </p>
                  <p className="text-muted-foreground text-sm">
                    Supports JPG, PNG, WebP
                  </p>
                </div>
              )}
            </div>

            <button
              onClick={analyzeImage}
              disabled={!selectedFile || loading}
              className="w-full mt-4 bg-primary text-primary-foreground py-3 px-6 rounded-xl font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Shield className="w-5 h-5" />
                  Analyze Animal
                </>
              )}
            </button>

            {error && (
              <div className="mt-4 p-4 bg-endangered/10 border border-endangered/20 rounded-xl text-endangered flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}

            {/* SDG Info Card */}
            <div className="mt-6 p-5 bg-card rounded-2xl border shadow-sm">
              <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                <Globe className="w-5 h-5" />
                About SDG 15: Life on Land
              </h3>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Protect, restore and promote sustainable use of terrestrial
                ecosystems, sustainably manage forests, combat desertification,
                and halt and reverse land degradation and halt biodiversity
                loss.
              </p>
              <div className="mt-4 grid grid-cols-3 gap-3 text-center">
                <div className="p-3 bg-secondary rounded-xl">
                  <p className="text-xl font-bold text-primary">1M+</p>
                  <p className="text-xs text-muted-foreground">
                    Species at risk
                  </p>
                </div>
                <div className="p-3 bg-secondary rounded-xl">
                  <p className="text-xl font-bold text-primary">75%</p>
                  <p className="text-xs text-muted-foreground">Land altered</p>
                </div>
                <div className="p-3 bg-secondary rounded-xl">
                  <p className="text-xl font-bold text-primary">40%</p>
                  <p className="text-xs text-muted-foreground">
                    Amphibian decline
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div>
            {analysis ? (
              analysis.not_animal ? (
                <div className="p-6 bg-card rounded-2xl border shadow-sm">
                  <div className="flex items-center gap-3 text-vulnerable mb-3">
                    <AlertTriangle className="w-6 h-6" />
                    <h3 className="font-semibold text-lg">No Animal Detected</h3>
                  </div>
                  <p className="text-muted-foreground">
                    {analysis.message ||
                      "Please upload an image containing an animal."}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Animal Info Header */}
                  <div className="p-6 bg-card rounded-2xl border shadow-sm">
                    <h2 className="text-2xl font-bold text-primary">
                      {analysis.animal_name || "Unknown Animal"}
                    </h2>
                    <p className="text-muted-foreground italic mb-4">
                      {analysis.scientific_name}
                    </p>

                    <div className="flex flex-wrap gap-3">
                      <span
                        className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusStyle(
                          analysis.conservation_status
                        )}`}
                      >
                        {analysis.conservation_status || "Unknown Status"}
                      </span>
                    </div>

                    <div className="mt-4 grid grid-cols-2 gap-4">
                      <div className="p-3 bg-secondary rounded-xl">
                        <p className="text-xs text-muted-foreground mb-1">
                          Population Trend
                        </p>
                        <div className="flex items-center gap-2">
                          {getTrendIcon(analysis.population_trend)}
                          <span className="font-medium">
                            {analysis.population_trend || "Unknown"}
                          </span>
                        </div>
                      </div>
                      <div className="p-3 bg-secondary rounded-xl">
                        <p className="text-xs text-muted-foreground mb-1">
                          Est. Population
                        </p>
                        <p className="font-medium">
                          {analysis.estimated_population || "Unknown"}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Tabs */}
                  <div className="flex gap-1 p-1 bg-secondary rounded-xl">
                    {tabs.map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-lg text-sm font-medium transition-all ${
                          activeTab === tab.id
                            ? "bg-card text-primary shadow-sm"
                            : "text-muted-foreground hover:text-foreground"
                        }`}
                      >
                        <tab.icon className="w-4 h-4" />
                        <span className="hidden sm:inline">{tab.label}</span>
                      </button>
                    ))}
                  </div>

                  {/* Tab Content */}
                  <div className="p-6 bg-card rounded-2xl border shadow-sm">
                    {activeTab === "background" && (
                      <div>
                        <h3 className="font-semibold text-primary mb-3">
                          About This Animal
                        </h3>
                        <p className="text-muted-foreground leading-relaxed">
                          {analysis.background || "No information available."}
                        </p>
                      </div>
                    )}

                    {activeTab === "habitat" && (
                      <div className="space-y-4">
                        <div>
                          <h3 className="font-semibold text-primary mb-3">
                            Habitat
                          </h3>
                          <p className="text-muted-foreground leading-relaxed">
                            {analysis.habitat || "No information available."}
                          </p>
                        </div>
                        <div>
                          <h3 className="font-semibold text-endangered mb-3">
                            Threats
                          </h3>
                          <p className="text-muted-foreground leading-relaxed">
                            {analysis.threats || "No information available."}
                          </p>
                        </div>
                      </div>
                    )}

                    {activeTab === "sdg" && (
                      <div>
                        <h3 className="font-semibold text-primary mb-3">
                          Connection to SDG 15: Life on Land
                        </h3>
                        <p className="text-muted-foreground leading-relaxed mb-4">
                          {analysis.sdg_connection ||
                            "No information available."}
                        </p>
                        <div className="p-4 bg-safe/10 border border-safe/20 rounded-xl">
                          <p className="text-sm text-safe font-medium">
                            SDG 15 aims to protect, restore and promote
                            sustainable use of terrestrial ecosystems and halt
                            biodiversity loss.
                          </p>
                        </div>
                      </div>
                    )}

                    {activeTab === "conservation" && (
                      <div className="space-y-4">
                        <div>
                          <h3 className="font-semibold text-primary mb-3">
                            Conservation Efforts
                          </h3>
                          <p className="text-muted-foreground leading-relaxed">
                            {analysis.conservation_efforts ||
                              "No information available."}
                          </p>
                        </div>
                        <div>
                          <h3 className="font-semibold text-primary mb-3">
                            How You Can Help
                          </h3>
                          <ul className="space-y-2 text-muted-foreground">
                            <li className="flex items-start gap-2">
                              <Heart className="w-4 h-4 text-primary mt-1 flex-shrink-0" />
                              Support conservation organizations
                            </li>
                            <li className="flex items-start gap-2">
                              <Heart className="w-4 h-4 text-primary mt-1 flex-shrink-0" />
                              Reduce your environmental footprint
                            </li>
                            <li className="flex items-start gap-2">
                              <Heart className="w-4 h-4 text-primary mt-1 flex-shrink-0" />
                              Spread awareness about endangered species
                            </li>
                            <li className="flex items-start gap-2">
                              <Heart className="w-4 h-4 text-primary mt-1 flex-shrink-0" />
                              Make sustainable consumer choices
                            </li>
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )
            ) : (
              <div className="h-full flex flex-col justify-center">
                <div className="p-6 bg-card rounded-2xl border shadow-sm text-center">
                  <Leaf className="w-16 h-16 mx-auto text-primary/30 mb-4" />
                  <h3 className="font-semibold text-lg mb-2">
                    Ready to Scan
                  </h3>
                  <p className="text-muted-foreground">
                    Upload an image of any animal to learn about its
                    conservation status and how it connects to SDG 15.
                  </p>
                </div>

                <div className="mt-6 p-5 bg-card rounded-2xl border shadow-sm">
                  <h3 className="font-semibold text-primary mb-3">
                    How It Works
                  </h3>
                  <ol className="space-y-3 text-sm text-muted-foreground">
                    <li className="flex gap-3">
                      <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold flex-shrink-0">
                        1
                      </span>
                      Upload an image of any animal
                    </li>
                    <li className="flex gap-3">
                      <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold flex-shrink-0">
                        2
                      </span>
                      Our AI identifies the species
                    </li>
                    <li className="flex gap-3">
                      <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold flex-shrink-0">
                        3
                      </span>
                      Learn about its conservation status
                    </li>
                    <li className="flex gap-3">
                      <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold flex-shrink-0">
                        4
                      </span>
                      Discover its connection to SDG 15
                    </li>
                  </ol>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-primary text-primary-foreground mt-12 py-6">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p className="text-sm">
            Supporting{" "}
            <a
              href="https://sdgs.un.org/goals/goal15"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-safe"
            >
              UN SDG 15: Life on Land
            </a>
          </p>
          <p className="text-xs text-primary-foreground/70 mt-2">
            Upload animal images to learn about conservation. Together we can
            protect biodiversity.
          </p>
        </div>
      </footer>
    </div>
  );
}
