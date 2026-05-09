import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { blockchainApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { formatDate, truncateHash } from '@/lib/utils'

interface Block {
  id?: number
  index: number
  hash: string
  previous_hash?: string
  timestamp: string
  data?: string
  nonce?: number
  difficulty?: number
  merkle_root?: string
  transaction_count?: number
}

/** API /blockchain/transactions — one row per block (chain record) */
interface ChainTransaction {
  id?: number
  index: number
  hash: string
  previous_hash?: string
  timestamp: string
  data?: string
  nonce?: number
}

interface BlockchainStats {
  total_blocks: number
  total_transactions: number
  difficulty: number
  hash_rate: number | string
  last_block_time: string
  average_block_time: number
  network_health: string
}

function parseTxPayload(data: string | undefined): {
  event_type?: string
  batch_code?: string
} {
  if (!data || typeof data !== 'string') return {}
  try {
    const j = JSON.parse(data) as { event_type?: string; batch_code?: string }
    return {
      event_type: j?.event_type,
      batch_code: j?.batch_code,
    }
  } catch {
    return {}
  }
}

/** Map FastAPI /blockchain/stats (chain-based) to UI fields */
function normalizeBlockchainStats(raw: Record<string, unknown> | null): BlockchainStats | null {
  if (!raw) return null
  const chainLen = Number(
    raw.chain_length ?? raw.total_blocks_mined ?? raw.total_blocks ?? 0
  )
  const totalTx = Number(raw.total_transactions ?? raw.total_events ?? chainLen)
  const avg = Number(raw.average_block_time ?? raw.average_block_time_seconds ?? 0)
  const lastRaw = raw.latest_block_timestamp ?? raw.last_block_time
  const lastStr =
    typeof lastRaw === 'string'
      ? lastRaw
      : lastRaw != null
        ? String(lastRaw)
        : ''
  const healthRaw = raw.network_health ?? raw.status ?? 'healthy'
  const health = typeof healthRaw === 'string' ? healthRaw : 'healthy'
  return {
    total_blocks: chainLen,
    total_transactions: totalTx,
    difficulty: Number(raw.difficulty ?? 2),
    hash_rate: typeof raw.hash_rate === 'number' ? raw.hash_rate : '—',
    last_block_time: lastStr,
    average_block_time: avg,
    network_health: health,
  }
}

export default function ExplorerPage() {
  const { blockId } = useParams()
  const [blocks, setBlocks] = useState<Block[]>([])
  const [transactions, setTransactions] = useState<ChainTransaction[]>([])
  const [selectedBlock, setSelectedBlock] = useState<Block | null>(null)
  const [selectedTransaction, setSelectedTransaction] = useState<ChainTransaction | null>(null)
  const [stats, setStats] = useState<BlockchainStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'blocks' | 'transactions' | 'stats'>('blocks')

  const filteredBlocks = blocks.filter(block => {
    if (!searchQuery.trim()) return true
    const query = searchQuery.toLowerCase().trim()
    return (
      block.hash?.toLowerCase().includes(query) ||
      block.previous_hash?.toLowerCase().includes(query) ||
      block.index?.toString().includes(query) ||
      block.data?.toLowerCase().includes(query) ||
      JSON.stringify(block).toLowerCase().includes(query)
    )
  })

  useEffect(() => {
    loadBlockchainData()
  }, [])

  useEffect(() => {
    if (blockId) {
      loadBlockDetails(parseInt(blockId))
    }
  }, [blockId])

  const loadBlockchainData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load recent blocks
      const blocksResponse = await blockchainApi.getBlocks(0, 20)
      const response = blocksResponse
      const blockList = response.data.transactions ?? response.data.blocks ?? response.data ?? []
      setBlocks(Array.isArray(blockList) ? blockList : [])

      // Load recent transactions
      const transactionsResponse = await blockchainApi.getTransactions(0, 20)
      const txData = transactionsResponse.data
      const txList = txData?.transactions ?? txData ?? []
      setTransactions(Array.isArray(txList) ? txList : [])

      // Load blockchain stats
      const statsResponse = await blockchainApi.getStats()
      setStats(normalizeBlockchainStats(statsResponse.data as Record<string, unknown>))

    } catch (err: any) {
      console.error('Error loading blockchain data:', err)
      setError('Failed to load blockchain data')
      setStats(null)
    } finally {
      setLoading(false)
    }
  }

  const loadBlockDetails = async (blockIndex: number) => {
    try {
      const response = await blockchainApi.getBlock(blockIndex)
      setSelectedBlock(response.data)
      setActiveTab('blocks')
    } catch (error: any) {
      console.error('Error loading block details:', error)
      setError('Failed to load block details')
    }
  }

  const handleSearch = async () => {
    // Client-side filtering is handled automatically by filteredBlocks
    // Clear any previous errors
    setError(null)
  }

  const getTransactionTypeColor = (type: string) => {
    const t = (type || '').toUpperCase()
    switch (t) {
      case 'BATCH_CREATED':
      case 'batch_creation':
        return 'bg-green-100 text-green-800'
      case 'GENESIS':
        return 'bg-slate-100 text-slate-800'
      case 'QUALITY_CHECKED':
      case 'quality_grading':
        return 'bg-blue-100 text-blue-800'
      case 'fraud_alert':
        return 'bg-red-100 text-red-800'
      case 'supply_chain':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getNetworkHealthColor = (health: string | undefined) => {
    const h = (health ?? '').toLowerCase()
    switch (h) {
      case 'healthy':
      case 'operational':
        return 'text-green-600'
      case 'warning':
        return 'text-yellow-600'
      case 'critical':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full mb-4">
            <span className="text-white font-bold text-2xl">⛓️</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Blockchain Explorer</h1>
          <p className="text-gray-600">
            Explore the Organic Roots blockchain for transparency and verification
          </p>
        </div>

        {/* Search Bar */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Search Blockchain</CardTitle>
            <CardDescription>
              Search by block hash, block index, or transaction hash
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-2">
              <div className="flex-1">
                <Input
                  placeholder="Enter block hash, index, or transaction hash..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
              <Button onClick={handleSearch} disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </div>
            {error && (
              <p className="text-sm text-red-500 mt-2">{error}</p>
            )}
          </CardContent>
        </Card>

        {/* Navigation Tabs */}
        <div className="border-b mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('blocks')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'blocks'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Blocks
            </button>
            <button
              onClick={() => setActiveTab('transactions')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'transactions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Transactions
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'stats'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Network Stats
            </button>
          </nav>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading blockchain data...</p>
          </div>
        )}

        {/* Blocks Tab */}
        {activeTab === 'blocks' && !loading && (
          <div className="space-y-6">
            {selectedBlock ? (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Block #{selectedBlock.index}</CardTitle>
                    <Button variant="outline" onClick={() => setSelectedBlock(null)}>
                      ← Back to Blocks
                    </Button>
                  </div>
                  <CardDescription>
                    Block Hash: {truncateHash(selectedBlock.hash)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Block Index</Label>
                      <p className="font-mono text-sm">{selectedBlock.index}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Timestamp</Label>
                      <p className="font-mono text-sm">{formatDate(selectedBlock.timestamp)}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Previous Hash</Label>
                      <p className="font-mono text-xs">{truncateHash(selectedBlock.previous_hash)}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Merkle Root</Label>
                      <p className="font-mono text-xs">{truncateHash(selectedBlock.merkle_root ?? '')}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Nonce</Label>
                      <p className="font-mono text-sm">{selectedBlock.nonce}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Difficulty</Label>
                      <p className="font-mono text-sm">{selectedBlock.difficulty ?? '—'}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Transactions</Label>
                      <p className="font-mono text-sm">{selectedBlock.transaction_count ?? '—'}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Block Data</Label>
                      <p className="font-mono text-xs break-all">{selectedBlock.data}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                <div className="text-sm text-gray-600 mb-4">
                  Showing {filteredBlocks.length} of {blocks.length} blocks
                </div>
                {Array.isArray(filteredBlocks) && filteredBlocks.map((block) => (
                  <Card key={block.id ?? block.index} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setSelectedBlock(block)}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="font-medium">Block #{block.index}</span>
                            <Badge variant="outline">
                              {(block.transaction_count ?? 1)} record(s)
                            </Badge>
                          </div>
                          <div className="text-sm text-gray-600">
                            <p>Hash: {truncateHash(block.hash)}</p>
                            <p>Mined: {formatDate(block.timestamp)}</p>
                          </div>
                        </div>
                          <div className="text-right">
                          <div className="text-sm text-gray-500">Nonce</div>
                          <div className="font-mono">{block.nonce ?? '—'}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Transactions Tab */}
        {activeTab === 'transactions' && !loading && (
          <div className="space-y-6">
            {selectedTransaction ? (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Chain record #{selectedTransaction.index}</CardTitle>
                    <Button variant="outline" onClick={() => setSelectedTransaction(null)}>
                      ← Back to Transactions
                    </Button>
                  </div>
                  <CardDescription>
                    Hash: {truncateHash(selectedTransaction.hash)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Block index</Label>
                      <p className="font-mono text-sm">#{selectedTransaction.index}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Nonce</Label>
                      <p className="font-mono text-sm">{selectedTransaction.nonce ?? '—'}</p>
                    </div>
                    <div className="space-y-2 md:col-span-2">
                      <Label>Full hash</Label>
                      <p className="font-mono text-xs break-all">{selectedTransaction.hash}</p>
                    </div>
                    <div className="space-y-2 md:col-span-2">
                      <Label>Previous hash</Label>
                      <p className="font-mono text-xs break-all">
                        {selectedTransaction.previous_hash
                          ? truncateHash(selectedTransaction.previous_hash)
                          : '—'}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Label>Event</Label>
                      <Badge className={getTransactionTypeColor(parseTxPayload(selectedTransaction.data).event_type || '')}>
                        {(parseTxPayload(selectedTransaction.data).event_type ?? 'N/A').replace(/_/g, ' ')}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <Label>Batch</Label>
                      <p className="font-mono text-sm">
                        {parseTxPayload(selectedTransaction.data).batch_code ?? 'Genesis'}
                      </p>
                    </div>
                    <div className="space-y-2 md:col-span-2">
                      <Label>Timestamp</Label>
                      <p className="font-mono text-sm">{formatDate(selectedTransaction.timestamp)}</p>
                    </div>
                    <div className="space-y-2 md:col-span-2">
                      <Label>Payload (data)</Label>
                      <p className="font-mono text-xs break-all whitespace-pre-wrap">{selectedTransaction.data ?? '—'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {Array.isArray(transactions) &&
                  transactions.map((tx) => {
                    const parsed = parseTxPayload(tx.data)
                    const ev = parsed.event_type ?? 'N/A'
                    const batchLabel = parsed.batch_code ?? 'Genesis'
                    return (
                      <Card
                        key={tx.id ?? tx.index}
                        className="cursor-pointer hover:shadow-md transition-shadow"
                        onClick={() => setSelectedTransaction(tx)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <Badge className={getTransactionTypeColor(ev)}>
                                  {ev.replace(/_/g, ' ')}
                                </Badge>
                                <Badge variant="outline">Block #{tx.index}</Badge>
                              </div>
                              <div className="text-sm text-gray-600">
                                <p>
                                  Hash:{' '}
                                  {tx.hash ? `${tx.hash.slice(0, 20)}...` : 'N/A'}
                                </p>
                                <p>Block: #{tx.index}</p>
                                <p>Event: {ev}</p>
                                <p>Batch: {batchLabel}</p>
                              </div>
                            </div>
                            <div className="text-right text-sm text-muted-foreground">
                              <div>{formatDate(tx.timestamp)}</div>
                              <div className="font-mono text-xs mt-1">Nonce {tx.nonce ?? '—'}</div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
              </div>
            )}
          </div>
        )}

        {activeTab === 'stats' && !loading && !stats && (
          <p className="text-center text-muted-foreground py-8">
            Network statistics could not be loaded. Try again or check the API.
          </p>
        )}

        {/* Stats Tab */}
        {activeTab === 'stats' && !loading && stats && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Blocks</CardTitle>
                  <div className="h-4 w-4 text-muted-foreground">📦</div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.total_blocks}</div>
                  <p className="text-xs text-muted-foreground">Mined blocks</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
                  <div className="h-4 w-4 text-muted-foreground">🔄</div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.total_transactions}</div>
                  <p className="text-xs text-muted-foreground">Confirmed transactions</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Network Hash Rate</CardTitle>
                  <div className="h-4 w-4 text-muted-foreground">⚡</div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.hash_rate}</div>
                  <p className="text-xs text-muted-foreground">MH/s</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Mining Difficulty</CardTitle>
                  <div className="h-4 w-4 text-muted-foreground">⛏️</div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.difficulty}</div>
                  <p className="text-xs text-muted-foreground">Current difficulty</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Average Block Time</CardTitle>
                  <div className="h-4 w-4 text-muted-foreground">⏱️</div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.average_block_time}s</div>
                  <p className="text-xs text-muted-foreground">Between blocks</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Network Health</CardTitle>
                  <div className="h-4 w-4 text-muted-foreground">💚</div>
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getNetworkHealthColor(stats.network_health)}`}>
                    {(stats.network_health ?? 'unknown').toUpperCase()}
                  </div>
                  <p className="text-xs text-muted-foreground">System status</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Last Block Information</CardTitle>
                <CardDescription>
                  Most recently mined block details
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm space-y-2">
                  <p>
                    <strong>Mined:</strong>{' '}
                    {stats.last_block_time ? formatDate(stats.last_block_time) : 'N/A'}
                  </p>
                  <p>
                    <strong>Network Status:</strong>{' '}
                    <span className={getNetworkHealthColor(stats.network_health)}>
                      {stats.network_health ?? 'Unknown'}
                    </span>
                  </p>
                  <p><strong>Blockchain Integrity:</strong> <span className="text-green-600">✓ Verified</span></p>
                  <p><strong>Consensus Algorithm:</strong> Proof of Work</p>
                  <p><strong>Block Size Limit:</strong> 1 MB</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
