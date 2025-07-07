# 个人财务管理系统 - 前端

基于 React + TypeScript + Vite 构建的个人财务管理系统前端应用。

## 环境变量配置

### 必需配置

创建 `.env` 文件并配置以下环境变量：

```bash
# API基础URL配置
VITE_API_BASE_URL=https://your-backend-domain.railway.app/api/v1
```

### 环境变量说明

- `VITE_API_BASE_URL`: 后端API服务地址
  - 开发环境: `http://localhost:8000/api/v1`
  - 生产环境: `https://your-backend-domain.railway.app/api/v1`

### 可选配置

```bash
# 应用标题
VITE_APP_TITLE=个人财务管理系统

# 调试模式
VITE_DEBUG_MODE=true
```

## 开发环境

```bash
npm install
npm run dev
```

## 生产构建

```bash
npm run build
npm run preview
```

## Railway 部署

在 Railway 前端 service 的环境变量中设置：

```
VITE_API_BASE_URL=https://your-backend-domain.railway.app/api/v1
```

## 技术栈

- React 18
- TypeScript
- Vite
- Ant Design
- Axios

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      ...tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      ...tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      ...tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
