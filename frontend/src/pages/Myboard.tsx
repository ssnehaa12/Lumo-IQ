import { useState, useEffect } from "react";
import { Trash2, Plus, Code, ChevronDown, ChevronUp, Circle, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface ListItem {
  name: string;
  value: string;
}

interface PinnedItem {
  id?: string;
  type: string;
  title?: string;
  text?: string;
  value?: string;
  metric?: string;
  your_value?: number;
  industry_avg?: number;
  gap?: number;
  status?: string;
  message?: string;
  impact?: string;
  segment?: string;
  avg_cost?: number;
  member_count?: number;
  pinnedAt: string;
  left_label?: string;
  left_value?: string;
  right_label?: string;
  right_value?: string;
  items?: ListItem[];
  sql?: string;
  query?: string;
}

interface MetricData {
  title: string;
  status: string;
  statusType: "low" | "moderate" | "high" | "critical";
  description: string;
  value?: number;
  displayType: "progress" | "score" | "ring";
  change?: string;
  trend?: "up" | "down" | "neutral";
  loading?: boolean;
  error?: boolean;
}

const dashboardTemplates = [
  { id: "executive", label: "Executive Summary" },
  { id: "clinical", label: "Clinical Insights" },
  { id: "financial", label: "Financial Analysis" },
];

const MyBoard = () => {
  // Analysis section state
  const [selectedTemplate, setSelectedTemplate] = useState<string>("executive");
  const [timePeriod, setTimePeriod] = useState<string>("90");
  const [metricsData, setMetricsData] = useState<Record<string, MetricData[]>>({
    executive: [],
    clinical: [],
    financial: []
  });
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);

  // My Board section state
  const [pinnedItems, setPinnedItems] = useState<PinnedItem[]>([]);
  const [customQuery, setCustomQuery] = useState("");
  const [generating, setGenerating] = useState(false);
  const [showSQL, setShowSQL] = useState<{[key: string]: boolean}>({});

  useEffect(() => {
    loadPinnedItems();
  }, []);

  // Analysis section functions - NOW FULLY AGENTIC
  const loadMetrics = async () => {
    setLoadingAnalysis(true);
    setHasGenerated(true);

    try {
      console.log(`Loading ${selectedTemplate} metrics for last ${timePeriod} days...`);
      
      // Call the AGENTIC backend endpoint
      const response = await fetch('http://localhost:8000/api/analysis/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template: selectedTemplate,
          days: parseInt(timePeriod)
        })
      });

      const data = await response.json();
      
      if (data.success && data.metrics) {
        console.log(`✅ Received ${data.metrics.length} metrics for ${selectedTemplate}`);
        
        // Store metrics for this template
        setMetricsData(prev => ({
          ...prev,
          [selectedTemplate]: data.metrics
        }));
      } else {
        console.error('Failed to load metrics:', data.error);
        
        // Fallback error state
        setMetricsData(prev => ({
          ...prev,
          [selectedTemplate]: [{
            title: "Data Loading Error",
            status: "Error",
            statusType: "critical",
            description: "Unable to load metrics. Please refresh the page.",
            value: 0,
            displayType: "progress",
            error: true
          }]
        }));
      }
    } catch (error) {
      console.error('Failed to load metrics:', error);
      
      setMetricsData(prev => ({
        ...prev,
        [selectedTemplate]: [{
          title: "Connection Error",
          status: "Error",
          statusType: "critical",
          description: "Cannot connect to backend. Please check API is running.",
          value: 0,
          displayType: "progress",
          error: true
        }]
      }));
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const getStatusClass = (type: string) => {
    switch (type) {
      case "low": return "status-low";
      case "moderate": return "status-moderate";
      case "high": return "status-high";
      case "critical": return "status-critical";
      default: return "status-moderate";
    }
  };

  const renderMetricDisplay = (metric: MetricData) => {
    if (metric.error) {
      return (
        <div className="mt-4 p-3 bg-destructive/10 border border-destructive/30 rounded-lg">
          <p className="text-sm text-destructive">Failed to load data</p>
        </div>
      );
    }
  
    switch (metric.displayType) {
      case "progress":
        return (
          <div className="mt-4">
            <Progress value={metric.value || 0} className="h-2" />
            <div className="flex justify-between mt-2 text-sm text-muted-foreground">
              <span>Current</span>
              <span>{metric.value?.toFixed(1)}%</span>
            </div>
          </div>
        );
      case "score":
        // Don't show /10 - just show as large number
        return null;
      case "ring":
        return (
          <div className="mt-4 flex justify-center">
            <div className="relative w-20 h-20">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  className="text-muted"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeDasharray={`${metric.value || 0}, 100`}
                  className="text-primary"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-bold">{metric.value?.toFixed(1)}</span>
                <span className="text-xs text-muted-foreground">%</span>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  // My Board section functions
  const loadPinnedItems = () => {
    const saved = localStorage.getItem('myboard_items');
    if (saved) {
      setPinnedItems(JSON.parse(saved));
    }
  };

  const removeItem = (index: number) => {
    const updated = pinnedItems.filter((_, i) => i !== index);
    setPinnedItems(updated);
    localStorage.setItem('myboard_items', JSON.stringify(updated));
  };

  const toggleSQL = (id: string) => {
    setShowSQL(prev => ({...prev, [id]: !prev[id]}));
  };

  const generateCustomWidget = async () => {
    if (!customQuery.trim()) return;

    setGenerating(true);
    try {
      const res = await fetch('http://localhost:8000/api/myboard/generate-widget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: customQuery })
      });

      const data = await res.json();
      
      if (data.success) {
        const newItem: PinnedItem = {
          ...data.widget,
          pinnedAt: new Date().toISOString()
        };
        
        const updated = [...pinnedItems, newItem];
        setPinnedItems(updated);
        localStorage.setItem('myboard_items', JSON.stringify(updated));
        setCustomQuery("");
      }
    } catch (error) {
      console.error('Failed to generate widget:', error);
    } finally {
      setGenerating(false);
    }
  };

  const SQLDisplay = ({ sql, id }: { sql?: string, id: string }) => {
    if (!sql) return null;
    
    return (
      <div className="mt-3 pt-3 border-t border-border">
        <button
          onClick={() => toggleSQL(id)}
          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <Code className="w-3 h-3" />
          <span>View SQL Query</span>
          {showSQL[id] ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
        
        {showSQL[id] && (
          <pre className="mt-2 p-3 bg-black/30 rounded-lg text-xs text-green-400 overflow-x-auto border border-border">
            {sql}
          </pre>
        )}
      </div>
    );
  };

  const renderItem = (item: PinnedItem, index: number) => {
    const itemId = item.id || `item-${index}`;
    
    switch (item.type) {
      case 'comparison':
        return (
          <div className="metric-card">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-semibold text-foreground text-sm">{item.title}</h3>
              <Button size="sm" variant="ghost" onClick={() => removeItem(index)}>
                <Trash2 className="w-4 h-4 text-destructive" />
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-primary/10 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">{item.left_label}</div>
                <div className="text-xl font-bold text-primary">{item.left_value}</div>
              </div>
              <div className="text-center p-3 bg-destructive/10 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">{item.right_label}</div>
                <div className="text-xl font-bold text-destructive">{item.right_value}</div>
              </div>
            </div>
            <div className="text-xs text-muted-foreground mt-3">Last 90 days</div>
            <SQLDisplay sql={item.sql} id={itemId} />
          </div>
        );

      case 'list':
        return (
          <div className="metric-card">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-semibold text-foreground text-sm">{item.title}</h3>
              <Button size="sm" variant="ghost" onClick={() => removeItem(index)}>
                <Trash2 className="w-4 h-4 text-destructive" />
              </Button>
            </div>
            <div className="space-y-2">
              {item.items?.map((listItem, i) => (
                <div key={i} className="flex justify-between items-center py-2 border-b border-border last:border-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-primary bg-primary/10 w-5 h-5 rounded-full flex items-center justify-center">
                      {i + 1}
                    </span>
                    <span className="text-sm text-foreground">{listItem.name}</span>
                  </div>
                  <span className="text-sm font-semibold text-foreground">{listItem.value}</span>
                </div>
              ))}
            </div>
            <div className="text-xs text-muted-foreground mt-3">By avg cost per claim</div>
            <SQLDisplay sql={item.sql} id={itemId} />
          </div>
        );

      case 'single':
      case 'custom':
        return (
          <div className="metric-card">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold text-foreground text-sm">{item.title}</h3>
              <Button size="sm" variant="ghost" onClick={() => removeItem(index)}>
                <Trash2 className="w-4 h-4 text-destructive" />
              </Button>
            </div>
            <div className="text-3xl font-bold text-foreground mb-2">
              {item.value}
            </div>
            <div className="text-xs text-muted-foreground">
              Custom metric
            </div>
            <SQLDisplay sql={item.sql} id={itemId} />
          </div>
        );

      case 'insight':
        return (
          <div className="metric-card">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold text-foreground">Insight</h3>
              <Button size="sm" variant="ghost" onClick={() => removeItem(index)}>
                <Trash2 className="w-4 h-4 text-destructive" />
              </Button>
            </div>
            <p className="text-sm text-foreground mb-2">{item.text}</p>
            <p className="text-xs text-muted-foreground">
              <span className="font-semibold">Impact:</span> {item.impact}
            </p>
          </div>
        );

      case 'alert':
        return (
          <div className="metric-card border-l-4 border-l-destructive">
            <div className="flex justify-between items-start mb-2">
              <span className="status-badge status-high">ALERT</span>
              <Button size="sm" variant="ghost" onClick={() => removeItem(index)}>
                <Trash2 className="w-4 h-4 text-destructive" />
              </Button>
            </div>
            <h3 className="font-semibold text-foreground mb-2">{item.metric}</h3>
            <p className="text-sm text-muted-foreground">{item.message}</p>
          </div>
        );

      case 'benchmark':
        return (
          <div className="metric-card">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold text-sm">{item.metric}</h3>
              <Button size="sm" variant="ghost" onClick={() => removeItem(index)}>
                <Trash2 className="w-4 h-4 text-destructive" />
              </Button>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Your Org:</span>
                <span className="font-semibold">{item.your_value?.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Industry:</span>
                <span>{item.industry_avg?.toFixed(1)}%</span>
              </div>
              <div className={`flex justify-between text-sm font-semibold ${item.status === 'below' ? 'text-destructive' : 'text-primary'}`}>
                <span>Gap:</span>
                <span>{item.gap && item.gap > 0 ? '+' : ''}{item.gap?.toFixed(1)}pp</span>
              </div>
            </div>
          </div>
        );

      case 'cohort':
        return (
          <div className="metric-card">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold text-lg">{item.segment}</h3>
              <Button size="sm" variant="ghost" onClick={() => removeItem(index)}>
                <Trash2 className="w-4 h-4 text-destructive" />
              </Button>
            </div>
            <div className="text-3xl font-bold text-foreground mb-2">
              ${item.avg_cost?.toFixed(2)}
            </div>
            <div className="text-sm text-muted-foreground">
              {item.member_count?.toLocaleString()} members
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="animate-fade-in">
      {/* ========== ANALYSIS SECTION (AGENTIC KPI CARDS) ========== */}
      <div className="mb-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold gradient-title mb-2">Analysis</h1>
          <p className="text-muted-foreground">
            AI-generated analytics with period comparisons from BigQuery
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-4 mb-8">
          <div className="flex-1 min-w-[200px]">
            <label className="text-sm font-medium mb-2 block">Dashboard Template</label>
            <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {dashboardTemplates.map(t => (
                  <SelectItem key={t.id} value={t.id}>{t.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex-1 min-w-[200px]">
            <label className="text-sm font-medium mb-2 block">Time Period</label>
            <Select value={timePeriod} onValueChange={setTimePeriod}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7">Last 7 Days</SelectItem>
                <SelectItem value="30">Last 30 Days</SelectItem>
                <SelectItem value="90">Last 90 Days</SelectItem>
                <SelectItem value="180">Last 6 Months</SelectItem>
                <SelectItem value="365">Last Year</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-end">
            <Button onClick={loadMetrics} disabled={loadingAnalysis}>
              <Sparkles className="w-4 h-4 mr-2" />
              {loadingAnalysis ? 'Generating...' : 'Generate Analysis'}
            </Button>
          </div>
        </div>

        {/* KPI Cards - Agent Generated */}
        {!hasGenerated ? (
          <div className="text-center py-16 border-2 border-dashed border-border rounded-lg">
            <Sparkles className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg text-muted-foreground mb-2">Ready to generate insights</p>
            <p className="text-sm text-muted-foreground">
              Select a template and time period, then click "Generate Analysis"
            </p>
          </div>
        ) : loadingAnalysis ? (
          <div className="text-center py-12 text-muted-foreground">
            <div className="mb-3">Agent analyzing data for {selectedTemplate}...</div>
            <div className="text-sm">Querying last {timePeriod} days vs previous period</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {metricsData[selectedTemplate]?.map((metric, index) => (
              <div key={index} className="metric-card">
                <div className="flex items-start gap-3">
                  <Circle className="w-5 h-5 text-primary mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground">{metric.title}</h3>
                    <span className={`status-badge mt-1 ${getStatusClass(metric.statusType)}`}>
                      {metric.status}
                    </span>
                    <p className="text-sm text-muted-foreground mt-2">{metric.description}</p>
                    {metric.change && (
                      <p className="text-xs text-muted-foreground mt-2">{metric.change}</p>
                    )}
                    {renderMetricDisplay(metric)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ========== MY BOARD SECTION (CUSTOM WIDGETS) ========== */}
      <div className="border-t border-border pt-12 mt-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-2">Custom Analysis</h2>
          <p className="text-muted-foreground">
            Ask any question and create custom widgets
          </p>
        </div>

        <div className="mb-8">
          <div className="flex gap-2">
            <Input
              placeholder="Ask for any metric (e.g., 'Average cost for diabetes meds')..."
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && generateCustomWidget()}
              className="flex-1"
            />
            <Button onClick={generateCustomWidget} disabled={generating || !customQuery.trim()}>
              <Plus className="w-4 h-4 mr-2" />
              {generating ? 'Generating...' : 'Add Widget'}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Or pin items from Lumoboard page
          </p>
        </div>

        <div className="mb-8">
          <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wide">
            Example Queries
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {[
              "Average cost for diabetes medications",
              "Total spend on cardiovascular drugs",
              "Percentage of members on specialty meds",
              "Count of high-risk members over 70",
              "Average cost per member in Medicare",
              "Total cost for generic vs brand drugs",
              "Which 3 drugs have highest cost per claim",
              "How much did costs increase Q3 to Q4",
              "Members with 3 or more chronic conditions"
            ].map((example, i) => (
              <button
                key={i}
                onClick={() => setCustomQuery(example)}
                className="text-left p-3 bg-card border border-border rounded-lg text-sm text-muted-foreground hover:text-foreground hover:border-primary/50 transition-all"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {pinnedItems.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-muted-foreground mb-4">
              <p className="text-lg mb-2">No custom widgets yet</p>
              <p className="text-sm">Click an example query above, pin items from Lumoboard, or create custom widgets</p>
            </div>
            <Link to="/lumoboard">
              <Button variant="outline">
                Go to Lumoboard
              </Button>
            </Link>
          </div>
        ) : (
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wide">
              Your Pinned Widgets
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {pinnedItems.map((item, index) => (
                <div key={index}>
                  {renderItem(item, index)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyBoard;