import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Pin, RefreshCw, AlertTriangle, TrendingUp, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Insight {
  text: string;
  impact: string;
  action: string;
}

interface Alert {
  severity: string;
  metric: string;
  current: number;
  threshold: number;
  message: string;
  impact: string;
}

interface Benchmark {
  metric: string;
  your_value: number;
  industry_avg: number;
  gap: number;
  status: string;
}

interface Cohort {
  segment: string;
  member_count: number;
  avg_cost: number;
}

const Lumoboard = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [cohorts, setCohorts] = useState<Cohort[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingStatus, setLoadingStatus] = useState('');

  useEffect(() => {
    loadAllSections();
  }, []);

  const loadAllSections = async () => {
    setLoading(true);
    
    try {
      // Load sections ONE BY ONE so they appear progressively
      setLoadingStatus('Generating insights...');
      const insRes = await fetch('http://localhost:8000/api/lumoboard/insights', { method: 'POST' });
      const insData = await insRes.json();
      setInsights(insData.insights || []);

      setLoadingStatus('Checking alerts...');
      const alertRes = await fetch('http://localhost:8000/api/lumoboard/alerts', { method: 'POST' });
      const alertData = await alertRes.json();
      setAlerts(alertData.alerts || []);

      setLoadingStatus('Loading benchmarks...');
      const benchRes = await fetch('http://localhost:8000/api/lumoboard/benchmarks', { method: 'POST' });
      const benchData = await benchRes.json();
      setBenchmarks(benchData.benchmarks || []);

      setLoadingStatus('Analyzing cohorts...');
      const cohortRes = await fetch('http://localhost:8000/api/lumoboard/cohorts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ segment_by: 'plan_type' })
      });
      const cohortData = await cohortRes.json();
      setCohorts(cohortData.cohorts || []);
      
      setLoadingStatus('');
    } catch (error) {
      console.error('Failed to load Lumoboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePin = (item: any, type: string) => {
    const pinnedItems = JSON.parse(localStorage.getItem('myboard_items') || '[]');
    pinnedItems.push({ ...item, type, pinnedAt: new Date().toISOString() });
    localStorage.setItem('myboard_items', JSON.stringify(pinnedItems));
    
    alert('Pinned to My Board!');
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'high': return 'status-high';
      case 'critical': return 'status-critical';
      case 'warning': return 'status-moderate';
      default: return 'status-low';
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold gradient-title mb-2">Lumoboard</h1>
          <p className="text-muted-foreground">
            AI-generated intelligence from your pharmacy data
          </p>
        </div>
        <Button onClick={loadAllSections} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh All
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">
          {loadingStatus || 'Generating insights from BigQuery...'}
        </div>
      ) : (
        <>
          {/* AUTO-INSIGHTS */}
          <section className="mb-10">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-semibold">Auto-Generated Insights</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {insights.map((insight, i) => (
                <div key={i} className="metric-card">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-foreground">Insight {i + 1}</h3>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handlePin(insight, 'insight')}
                    >
                      <Pin className="w-4 h-4" />
                    </Button>
                  </div>
                  <p className="text-sm text-foreground mb-2">{insight.text}</p>
                  <p className="text-xs text-muted-foreground mb-1">
                    <span className="font-semibold">Impact:</span> {insight.impact}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    <span className="font-semibold">Action:</span> {insight.action}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* SMART ALERTS */}
          {alerts.length > 0 && (
            <section className="mb-10">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-5 h-5 text-destructive" />
                <h2 className="text-xl font-semibold">Smart Alerts</h2>
              </div>
              <div className="space-y-3">
                {alerts.map((alert, i) => (
                  <div key={i} className="metric-card border-l-4 border-l-destructive">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`status-badge ${getSeverityClass(alert.severity)}`}>
                            {alert.severity.toUpperCase()}
                          </span>
                          <h3 className="font-semibold">{alert.metric}</h3>
                        </div>
                        <p className="text-sm text-foreground mb-1">{alert.message}</p>
                        <p className="text-sm text-muted-foreground">
                          <span className="font-semibold">Impact:</span> {alert.impact}
                        </p>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handlePin(alert, 'alert')}
                      >
                        <Pin className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* BENCHMARKS */}
          <section className="mb-10">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-semibold">Industry Benchmarks</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {benchmarks.map((bench, i) => (
                <div key={i} className="metric-card">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-sm">{bench.metric}</h3>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handlePin(bench, 'benchmark')}
                    >
                      <Pin className="w-4 h-4" />
                    </Button>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Your Org:</span>
                      <span className="font-semibold">{bench.your_value.toFixed(1)}{bench.metric.includes('Rate') || bench.metric.includes('Proportion') ? '%' : ''}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Industry:</span>
                      <span>{bench.industry_avg.toFixed(1)}{bench.metric.includes('Rate') || bench.metric.includes('Proportion') ? '%' : ''}</span>
                    </div>
                    <div className={`flex justify-between text-sm font-semibold ${bench.status === 'below' ? 'text-destructive' : 'text-primary'}`}>
                      <span>Gap:</span>
                      <span>{bench.gap > 0 ? '+' : ''}{bench.gap.toFixed(1)}{bench.metric.includes('Rate') || bench.metric.includes('Proportion') ? 'pp' : ''}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* COHORT ANALYSIS */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-semibold">Cohort Analysis</h2>
              <span className="text-sm text-muted-foreground ml-2">(by Plan Type)</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {cohorts.map((cohort, i) => (
                <div key={i} className="metric-card cursor-pointer hover:border-primary/50 transition-all">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-lg">{cohort.segment}</h3>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handlePin(cohort, 'cohort')}
                    >
                      <Pin className="w-4 h-4" />
                    </Button>
                  </div>
                  <div className="space-y-2">
                    <div className="text-3xl font-bold text-foreground">
                      ${cohort.avg_cost.toFixed(2)}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Avg cost per claim
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {cohort.member_count.toLocaleString()} members
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
};

export default Lumoboard;