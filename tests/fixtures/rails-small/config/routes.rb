Rails.application.routes.draw do
  post "/session/refresh", to: "sessions#refresh"
end
