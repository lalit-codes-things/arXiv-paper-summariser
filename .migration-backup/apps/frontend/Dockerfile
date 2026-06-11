FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
COPY apps/frontend/package.json apps/frontend/package.json
RUN npm install

FROM deps AS builder
COPY apps/frontend apps/frontend
RUN npm --workspace apps/frontend run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/apps/frontend/.next/standalone ./
COPY --from=builder /app/apps/frontend/.next/static ./apps/frontend/.next/static
COPY --from=builder /app/apps/frontend/public ./apps/frontend/public
EXPOSE 3000
CMD ["node", "apps/frontend/server.js"]
