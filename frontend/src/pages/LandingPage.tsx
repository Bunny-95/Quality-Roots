import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 organic-gradient rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">OR</span>
            </div>
            <h1 className="text-xl font-bold organic-text">Organic Roots</h1>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/login">
              <Button variant="outline" size="sm">Sign In</Button>
            </Link>
            <Link to="/register">
              <Button size="sm" className="organic-gradient">Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <Badge className="mb-4 bg-green-100 text-green-800">
            AI-Enabled Agricultural Supply Chain
          </Badge>
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Trace Your Food From
            <span className="organic-text block">Farm to Table</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Experience complete transparency in your agricultural supply chain with our AI-powered 
            blockchain verification system. Know exactly where your food comes from.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button size="lg" className="organic-gradient">
                Start Your Journey
              </Button>
            </Link>
            <Link to="/verify">
              <Button variant="outline" size="lg">
                Verify Product
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h2>
          <p className="text-lg text-gray-600">Complete transparency at every step</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 organic-gradient rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl">🌱</span>
              </div>
              <CardTitle>Farmer Registration</CardTitle>
              <CardDescription>
                Farmers register their products and batches with detailed information
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 organic-gradient rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl">🤖</span>
              </div>
              <CardTitle>AI Quality Grading</CardTitle>
              <CardDescription>
                Advanced AI algorithms grade product quality and detect potential fraud
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 organic-gradient rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl">⛓️</span>
              </div>
              <CardTitle>Blockchain Verification</CardTitle>
              <CardDescription>
                Every transaction is recorded on our secure blockchain for complete traceability
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <Card className="max-w-2xl mx-auto">
          <CardContent className="text-center p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Ready to Join the Revolution?
            </h2>
            <p className="text-lg text-gray-600 mb-6">
              Whether you're a farmer, distributor, or consumer, Organic Roots has something for you.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register">
                <Button size="lg" className="organic-gradient">
                  Create Account
                </Button>
              </Link>
              <Link to="/verify">
                <Button variant="outline" size="lg">
                  Try Verification
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-sm text-gray-600">
            © 2026 Organic Roots. AI-enabled agricultural supply chain provenance.
          </div>
        </div>
      </footer>
    </div>
  )
}
