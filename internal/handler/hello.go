package handler

import (
	"net/http"
	"test-project/internal/model"
	"test-project/internal/service"

	"github.com/gin-gonic/gin"
)

func Hello(c *gin.Context) {
	msg := service.Hello()
	c.JSON(http.StatusOK, model.Response{
		Code:    0,
		Message: msg,
		Data:    nil,
	})
}
