export interface User {
  id: number
  identifier: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AccessTokenResponse {
  access_token: string
  token_type: string
}
