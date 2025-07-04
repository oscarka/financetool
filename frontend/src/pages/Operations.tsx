import React from 'react'
import FundOperations from '../components/FundOperations'

const Operations: React.FC = () => {
    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900">操作记录</h1>
                <p className="mt-2 text-sm text-gray-700">
                    记录您的投资操作和决策
                </p>
            </div>

            <FundOperations />
        </div>
    )
}

export default Operations 