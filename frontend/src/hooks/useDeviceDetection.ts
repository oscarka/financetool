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
            
            // 检测移动设备
            const isMobileDevice = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)
            
            // 基于屏幕宽度判断
            const isMobileWidth = width <= 768
            const isTabletWidth = width > 768 && width <= 1024

            // 综合判断
            const isMobile = isMobileDevice || isMobileWidth
            const isTablet = !isMobile && isTabletWidth
            const isDesktop = !isMobile && !isTablet

            const newDeviceInfo = {
                isMobile,
                isTablet,
                isDesktop,
                screenWidth: width
            }

            setDeviceInfo(newDeviceInfo)
        }

        // 初始检测
        updateDeviceInfo()

        // 使用防抖来减少resize事件的频率
        let resizeTimeout: NodeJS.Timeout
        const handleResize = () => {
            clearTimeout(resizeTimeout)
            resizeTimeout = setTimeout(updateDeviceInfo, 100)
        }

        // 监听窗口大小变化
        window.addEventListener('resize', handleResize)
        
        // 监听设备方向变化
        window.addEventListener('orientationchange', updateDeviceInfo)

        return () => {
            window.removeEventListener('resize', handleResize)
            window.removeEventListener('orientationchange', updateDeviceInfo)
            clearTimeout(resizeTimeout)
        }
    }, [])

    return deviceInfo
}