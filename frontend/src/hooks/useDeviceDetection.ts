import { useState, useEffect } from 'react'

interface DeviceInfo {
    isMobile: boolean
    isTablet: boolean
    isDesktop: boolean
    screenWidth: number
}

export const useDeviceDetection = (): DeviceInfo => {
    const [deviceInfo, setDeviceInfo] = useState<DeviceInfo>({
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        screenWidth: 1920
    })

    useEffect(() => {
        const updateDeviceInfo = () => {
            const width = window.innerWidth
            const userAgent = navigator.userAgent.toLowerCase()
            
            console.log('🔧 设备检测更新:', {
                windowWidth: width,
                userAgent: userAgent.substring(0, 100),
                timestamp: new Date().toISOString()
            })
            
            // 检测移动设备
            const isMobileDevice = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)
            
            // 基于屏幕宽度判断
            const isMobileWidth = width <= 768
            const isTabletWidth = width > 768 && width <= 1024

            // 综合判断
            const isMobile = isMobileDevice || isMobileWidth
            const isTablet = !isMobile && isTabletWidth
            const isDesktop = !isMobile && !isTablet

            console.log('🎯 设备判断结果:', {
                isMobileDevice,
                isMobileWidth,
                width,
                isMobile,
                isTablet,
                isDesktop
            })

            const newDeviceInfo = {
                isMobile,
                isTablet,
                isDesktop,
                screenWidth: width
            }

            setDeviceInfo(newDeviceInfo)
            
            console.log('✅ 设备信息已更新:', newDeviceInfo)
        }

        // 初始检测
        console.log('🚀 useDeviceDetection hook 初始化')
        updateDeviceInfo()

        // 监听窗口大小变化
        window.addEventListener('resize', updateDeviceInfo)
        
        // 监听设备方向变化
        window.addEventListener('orientationchange', updateDeviceInfo)

        return () => {
            console.log('🧹 useDeviceDetection hook 清理')
            window.removeEventListener('resize', updateDeviceInfo)
            window.removeEventListener('orientationchange', updateDeviceInfo)
        }
    }, [])

    return deviceInfo
}