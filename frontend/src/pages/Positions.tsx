import React from 'react'
import FundPositions from '../components/FundPositions'

const Positions: React.FC = () => {
    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900">持仓</h1>
                <p className="mt-2 text-sm text-gray-700">
                    查看当前所有资产的持仓状态
                </p>
            </div>

            <FundPositions />
        </div>
    )
}

export default Positions 