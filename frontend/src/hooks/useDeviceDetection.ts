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

            setDeviceInfo({
                isMobile,
                isTablet,
                isDesktop,
                screenWidth: width
            })
        }

        // 初始检测
        updateDeviceInfo()

        // 监听窗口大小变化
        window.addEventListener('resize', updateDeviceInfo)
        
        // 监听设备方向变化
        window.addEventListener('orientationchange', updateDeviceInfo)

        return () => {
            window.removeEventListener('resize', updateDeviceInfo)
            window.removeEventListener('orientationchange', updateDeviceInfo)
        }
    }, [])

    return deviceInfo
}