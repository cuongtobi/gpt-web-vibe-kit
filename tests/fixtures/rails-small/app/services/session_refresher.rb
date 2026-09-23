class SessionRefresher
  def self.call(refresh_token)
    { access_token: refresh_token, refreshed: true }
  end
end
