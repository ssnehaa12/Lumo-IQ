import { ArrowRight, Sparkles, Brain, TrendingUp, Zap, Database, Shield, BarChart3, Code } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Home = () => {
  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <div className="text-center mb-16 pt-8">
        <div className="mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full border border-primary/20 mb-6">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm text-primary font-medium">Agentic AI-Powered Analytics</span>
          </div>
        </div>
        
        <h1 className="text-5xl font-bold gradient-title mb-4">
          Lumo IQ
        </h1>
        
        <p className="text-xl text-muted-foreground mb-3 max-w-3xl mx-auto">
          Enterprise Pharmacy Analytics Platform
        </p>
        
        <p className="text-sm text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
          <span className="text-primary font-semibold">Lumo</span> (from Latin <em>lumen</em> - light) symbolizes clarity and intelligence. 
          Transform your pharmacy data into actionable insights with AI-powered decision intelligence.
        </p>

        <Link to="/lumoboard">
          <Button size="lg" className="gap-2">
            Get Started
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>

      {/* Key Features */}
      <div className="mb-16">
        <h2 className="text-2xl font-bold text-center mb-8">How Lumo IQ Works</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {/* Feature 1 */}
          <Link to="/lumoboard" className="block">
            <div className="metric-card hover:border-primary/50 transition-all cursor-pointer h-full">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <Brain className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground mb-2">Lumoboard</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    AI-generated strategic intelligence from your data
                  </p>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5" />
                      <span className="text-muted-foreground">Auto-generated insights updated regularly</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5" />
                      <span className="text-muted-foreground">Smart alerts when metrics exceed thresholds</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5" />
                      <span className="text-muted-foreground">Industry benchmark comparisons</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5" />
                      <span className="text-muted-foreground">Cohort analysis by plan type</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-border">
                    <span className="text-sm text-primary font-medium flex items-center gap-2">
                      View Strategic Insights <ArrowRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Link>

          {/* Feature 2 */}
          <Link to="/my-board" className="block">
            <div className="metric-card hover:border-primary/50 transition-all cursor-pointer h-full">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <Zap className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground mb-2">Analysis & Insights</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Custom analytics and interactive exploration
                  </p>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5" />
                      <span className="text-muted-foreground">Pre-built dashboard templates with period comparisons</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5" />
                      <span className="text-muted-foreground">Ask any question in natural language</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5" />
                      <span className="text-muted-foreground">Create custom widgets from queries</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5" />
                      <span className="text-muted-foreground">View SQL for complete transparency</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-border">
                    <span className="text-sm text-primary font-medium flex items-center gap-2">
                      Start Exploring <ArrowRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        </div>
      </div>

      {/* Platform Capabilities */}
      <div className="mb-16">
        <h2 className="text-2xl font-bold text-center mb-8">Platform Capabilities</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="metric-card text-center">
            <div className="inline-flex p-3 bg-primary/10 rounded-lg mb-4">
              <Database className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold text-foreground mb-2">50K+ Claims Analyzed</h3>
            <p className="text-sm text-muted-foreground">
              Real-time analytics on prescription claims, member demographics, and drug formulary data in BigQuery
            </p>
          </div>

          <div className="metric-card text-center">
            <div className="inline-flex p-3 bg-primary/10 rounded-lg mb-4">
              <TrendingUp className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold text-foreground mb-2">Decision Intelligence</h3>
            <p className="text-sm text-muted-foreground">
              Not just metrics get benchmarks, impact quantification, and recommended actions for every insight
            </p>
          </div>

          <div className="metric-card text-center">
            <div className="inline-flex p-3 bg-primary/10 rounded-lg mb-4">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold text-foreground mb-2">Transparent & Verifiable</h3>
            <p className="text-sm text-muted-foreground">
              View the SQL behind every metric. Full transparency into how insights are calculated and validated
            </p>
          </div>
        </div>
      </div>

      {/* Technical Foundation */}
      <div className="border-t border-border pt-12 mb-8">
        <h2 className="text-2xl font-bold text-center mb-8">Built for Enterprise</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-4">
            <div className="text-2xl font-bold text-primary mb-1">LangGraph</div>
            <div className="text-xs text-muted-foreground">ReAct Agent Framework</div>
          </div>
          
          <div className="text-center p-4">
            <div className="text-2xl font-bold text-primary mb-1">BigQuery</div>
            <div className="text-xs text-muted-foreground">Cloud Data Warehouse</div>
          </div>
          
          <div className="text-center p-4">
            <div className="text-2xl font-bold text-primary mb-1">RAG</div>
            <div className="text-xs text-muted-foreground">Vector Search</div>
          </div>
          
          <div className="text-center p-4">
            <div className="text-2xl font-bold text-primary mb-1">Claude 4</div>
            <div className="text-xs text-muted-foreground">Advanced Reasoning</div>
          </div>

          <div className="text-center p-4">
            <div className="text-2xl font-bold text-primary mb-1">FastAPI</div>
            <div className="text-xs text-muted-foreground">Python Backend</div>
          </div>
        </div>
      </div>

      {/* Footer */}
        <div className="text-center text-sm text-muted-foreground">
          <p className="mb-2">© 2026 Lumo IQ Platform</p>
          <p>Owned by <span className="text-foreground font-medium">Sneha Manjunath</span>. All rights reserved.</p>
        </div>
      </div>
  );
};

export default Home;