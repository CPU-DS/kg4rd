import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { Select, Button, Loading, Input, InputWithToken, Pagination } from '../Common'
import { linkService } from '../../services'
import type { LinkRequest, LinkResult, NodeType, RelationType } from '../../types'
import { ResultCode } from '../../types'
import { exportLinkResultToExcel, exportLinkResultToCSV } from '../../utils/exportUtils'

const LinkPrediction: React.FC = () => {
  const [modelNames, setModelNames] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState('')
  const [headType, setHeadType] = useState<'entities' | 'type'>('entities')
  const [headEntities, setHeadEntities] = useState('')
  const [headNodeType, setHeadNodeType] = useState<NodeType>('disease')
  const [tailType, setTailType] = useState<'entities' | 'type'>('entities')
  const [tailEntities, setTailEntities] = useState('')
  const [tailNodeType, setTailNodeType] = useState<NodeType>('drug')
  const [relationTypes, setRelationTypes] = useState<string[]>([])
  const [results, setResults] = useState<LinkResult>([])
  const [loading, setLoading] = useState(false)
  const [modelsLoading, setModelsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // 限制数量设置
  const [limitType, setLimitType] = useState<'unlimited' | 'custom'>('custom')
  const [customLimit, setCustomLimit] = useState('100')
  
  // 分页状态
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  const nodeTypeOptions = [
    { value: 'disease', label: '疾病' },
    { value: 'drug', label: '药物' },
    { value: 'gene/protein', label: '基因/蛋白质' },
    { value: 'pathway', label: '通路' },
    { value: 'effect/phenotype', label: '效应/表型' },
    { value: 'molecular_function', label: '分子功能' },
    { value: 'cellular_component', label: '细胞组分' },
    { value: 'biological_process', label: '生物过程' }
  ]

  const relationTypeOptions = [
    { value: 'drug_drug', label: '药物-药物' },
    { value: 'protein_protein', label: '蛋白质-蛋白质' },
    { value: 'disease_phenotype_positive', label: '疾病-表型(正向)' },
    { value: 'bioprocess_protein', label: '生物过程-蛋白质' },
    { value: 'cellcomp_protein', label: '细胞组分-蛋白质' },
    { value: 'molfunc_protein', label: '分子功能-蛋白质' },
    { value: 'phenotype_protein', label: '表型-蛋白质' },
    { value: 'disease_protein', label: '疾病-蛋白质' },
    { value: 'disease_disease', label: '疾病-疾病' },
    { value: 'drug_effect', label: '药物-效应' },
    { value: 'pathway_protein', label: '通路-蛋白质' },
    { value: 'bioprocess_bioprocess', label: '生物过程-生物过程' },
    { value: 'drug_protein', label: '药物-蛋白质' },
    { value: 'phenotype_phenotype', label: '表型-表型' },
    { value: 'contraindication', label: '禁忌症' },
    { value: 'molfunc_molfunc', label: '分子功能-分子功能' },
    { value: 'indication', label: '适应症' },
    { value: 'cellcomp_cellcomp', label: '细胞组分-细胞组分' },
    { value: 'drug_pathway', label: '药物-通路' },
    { value: 'pathway_pathway', label: '通路-通路' },
    { value: 'off-label use', label: '超说明书用药' },
    { value: 'disease_phenotype_negative', label: '疾病-表型(负向)' }
  ]

  const headTypeOptions = [
    { value: 'entities', label: '指定实体' },
    { value: 'type', label: '按类型' }
  ]

  const tailTypeOptions = [
    { value: 'entities', label: '指定实体' },
    { value: 'type', label: '按类型' }
  ]

  useEffect(() => {
    const loadModelNames = async () => {
      try {
        const response = await linkService.getModelNames()
        if (response.code === ResultCode.QUERY_OK) {
          setModelNames(response.data || [])
          if (response.data && response.data.length > 0) {
            setSelectedModel(response.data[0])
          }
        } else {
          setError('加载模型列表失败')
        }
      } catch (err) {
        setError('加载模型列表出错')
      } finally {
        setModelsLoading(false)
      }
    }

    loadModelNames()
  }, [])

  const handleRelationTypeChange = (tokens: string[]) => {
    setRelationTypes(tokens)
  }

  const handleLimitTypeChange = (type: 'unlimited' | 'custom') => {
    setLimitType(type)
  }

  const handleCustomLimitChange = (value: string) => {
    // 只允许输入数字
    if (value === '' || /^\d+$/.test(value)) {
      setCustomLimit(value)
    }
  }

  function truncateString(str: string, length = 40) {
    if (str.length <= length) {
      return str
    }
    return str.slice(0, length) + '...'
  }

  // 分页数据计算
  const paginatedResults = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    const endIndex = startIndex + pageSize
    return results.slice(startIndex, endIndex)
  }, [results, currentPage, pageSize])

  const totalPages = Math.ceil(results.length / pageSize)

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize)
    setCurrentPage(1) // 重置到第一页
  }

  // 重置分页状态
  const resetPagination = () => {
    setCurrentPage(1)
  }

  // 导出功能
  const handleExportExcel = () => {
    exportLinkResultToExcel(results)
  }

  const handleExportCSV = () => {
    exportLinkResultToCSV(results)
  }

  // 跳转到实体详情页
  const handleEntityClick = (nodeIndex: number) => {
    window.open(`/entity/${nodeIndex}`, '_blank', 'noopener,noreferrer')
  }

  const handlePredict = useCallback(async () => {
    if (!selectedModel) {
      setError('请选择预测模型')
      return
    }

    if (relationTypes.length === 0) {
      setError('请至少选择一种关系类型')
      return
    }

    if (limitType === 'custom' && (!customLimit || parseInt(customLimit) <= 0)) {
      setError('请输入有效的限制数量')
      return
    }

    let headParam: number[] | NodeType
    let tailParam: number[] | NodeType

    if (headType === 'entities') {
      if (!headEntities.trim()) {
        setError('请输入头实体索引')
        return
      }
      try {
        headParam = headEntities.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
        if (headParam.length === 0) {
          setError('头实体索引格式错误')
          return
        }
      } catch {
        setError('头实体索引格式错误')
        return
      }
    } else {
      headParam = headNodeType
    }

    if (tailType === 'entities') {
      if (!tailEntities.trim()) {
        setError('请输入尾实体索引')
        return
      }
      try {
        tailParam = tailEntities.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
        if (tailParam.length === 0) {
          setError('尾实体索引格式错误')
          return
        }
      } catch {
        setError('尾实体索引格式错误')
        return
      }
    } else {
      tailParam = tailNodeType
    }

    setLoading(true)
    setError(null)
    resetPagination() // 重置分页

    try {
      const request: LinkRequest = {
        head: headParam,
        rel: relationTypes as RelationType[],
        tail: tailParam,
        model_name: selectedModel,
        ...(limitType === 'custom' && customLimit ? { limit: parseInt(customLimit) } : {})
      }

      const response = await linkService.predict(request)
      
      if (response.code === ResultCode.QUERY_OK) {
        setResults(response.data || [])
      } else {
        setError(response.message || '预测失败')
      }
    } catch (err) {
      setError('预测出错，请稍后重试')
    } finally {
      setLoading(false)
    }
  }, [selectedModel, headType, headEntities, headNodeType, tailType, tailEntities, tailNodeType, relationTypes, limitType, customLimit])

  const getNodeTypeLabel = (type: string) => {
    const option = nodeTypeOptions.find(opt => opt.value === type)
    return option?.label || type
  }

  const getRelationTypeLabel = (type: string) => {
    const option = relationTypeOptions.find(opt => opt.value === type)
    return option?.label || type
  }

  if (modelsLoading) {
    return (
      <div className="flex justify-center py-8">
        <Loading size="lg" />
      </div>
    )
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* 预测配置 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">链接预测配置</h3>
        
        <div className="space-y-6">
          {/* 模型选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              预测模型
            </label>
            <Select
              value={selectedModel}
              onChange={setSelectedModel}
              options={modelNames.map(name => ({ value: name, label: name }))}
              placeholder="请选择模型"
            />
          </div>

          {/* 头实体配置 */}
          <div className="border border-gray-200 rounded-xl p-4">
            <h4 className="text-base font-medium text-gray-900 mb-4">头实体配置</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  配置方式
                </label>
                <Select
                  value={headType}
                  onChange={(value) => setHeadType(value as 'entities' | 'type')}
                  options={headTypeOptions}
                />
              </div>
              
              {headType === 'entities' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    实体索引 (多个用逗号分隔)
                  </label>
                  <Input
                    value={headEntities}
                    onChange={setHeadEntities}
                    placeholder="例如: 1,2,3"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    节点类型
                  </label>
                  <Select
                    value={headNodeType}
                    onChange={(value) => setHeadNodeType(value as NodeType)}
                    options={nodeTypeOptions}
                  />
                </div>
              )}
            </div>
          </div>

          {/* 尾实体配置 */}
          <div className="border border-gray-200 rounded-xl p-4">
            <h4 className="text-base font-medium text-gray-900 mb-4">尾实体配置</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  配置方式
                </label>
                <Select
                  value={tailType}
                  onChange={(value) => setTailType(value as 'entities' | 'type')}
                  options={tailTypeOptions}
                />
              </div>
              
              {tailType === 'entities' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    实体索引 (多个用逗号分隔)
                  </label>
                  <Input
                    value={tailEntities}
                    onChange={setTailEntities}
                    placeholder="例如: 1,2,3"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    节点类型
                  </label>
                  <Select
                    value={tailNodeType}
                    onChange={(value) => setTailNodeType(value as NodeType)}
                    options={nodeTypeOptions}
                  />
                </div>
              )}
            </div>
          </div>

          {/* 关系类型选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              关系类型 (已选择 {relationTypes.length} 个)
            </label>
            <InputWithToken
              selectedTokens={relationTypes}
              onChange={handleRelationTypeChange}
              options={relationTypeOptions}
              placeholder="选择或搜索关系类型..."
            />
          </div>

          {/* 结果数量限制 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              结果数量限制
            </label>
            <div className="space-y-3">
              <div className="flex items-center space-x-4">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="limitType"
                    value="unlimited"
                    checked={limitType === 'unlimited'}
                    onChange={() => handleLimitTypeChange('unlimited')}
                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">不限制</span>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="limitType"
                    value="custom"
                    checked={limitType === 'custom'}
                    onChange={() => handleLimitTypeChange('custom')}
                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">自定义数量</span>
                </label>
              </div>
              
              {limitType === 'custom' && (
                <div className="flex items-center space-x-3">
                  <Input
                    value={customLimit}
                    onChange={handleCustomLimitChange}
                    placeholder="输入数量"
                    className="w-24"
                  />
                  <span className="text-sm text-gray-500 whitespace-nowrap">条结果</span>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-center">
            <Button onClick={handlePredict} loading={loading} size="lg">
              开始预测
            </Button>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* 预测结果 */}
      {loading && (
        <div className="flex justify-center py-8">
          <Loading size="lg" />
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 animate-fade-in">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                预测结果 (共 {results.length} 条)
              </h3>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportExcel}
                    className="text-sm"
                  >
                    导出Excel
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportCSV}
                    className="text-sm"
                  >
                    导出CSV
                  </Button>
                </div>
                <div className="text-sm text-gray-500">
                  第 {currentPage} 页，共 {totalPages} 页
                </div>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    头实体
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    关系
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    尾实体
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    预测分数
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    类型
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedResults.map((result, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <button
                          onClick={() => handleEntityClick(result.x_index)}
                          className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline cursor-pointer text-left"
                        >
                          {truncateString(result.x_name)}
                        </button>
                        <div className="text-sm text-gray-500">
                          {getNodeTypeLabel(result.x_type)} | 索引: {result.x_index}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {getRelationTypeLabel(result.relation_name)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <button
                          onClick={() => handleEntityClick(result.y_index)}
                          className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline cursor-pointer text-left"
                        >
                          {truncateString(result.y_name)}
                        </button>
                        <div className="text-sm text-gray-500">
                          {getNodeTypeLabel(result.y_type)} | 索引: {result.y_index}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-gray-900 mr-2">
                          {result.score.toFixed(4)}
                        </div>
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${Math.min(result.score * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        result.type === 'present' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {result.type === 'present' ? result.uid ? `存在(${result.uid})`: '存在' : '不存在'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* 分页组件 */}
          <div className="px-6 py-4 border-t border-gray-200">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalItems={results.length}
              itemsPerPage={pageSize}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
              pageSizeOptions={[10, 20, 50, 100]}
            />
          </div>
        </div>
      )}

      {!loading && results.length === 0 && selectedModel && (
        <div className="text-center py-8 text-gray-500">
          暂无预测结果
        </div>
      )}
    </div>
  )
}

export default LinkPrediction