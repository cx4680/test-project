package goroutine

//func Server() {
//	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
//	defer cancel() // 确保资源释放
//
//	for i := 0; i < 3; i++ {
//		go worker(ctx, i)
//	}
//
//	time.Sleep(3 * time.Second) // 等待超时触发
//}
//
//func worker(ctx context.Context, id int) {
//	for {
//		select {
//		case <-ctx.Done(): // 监听取消信号
//			fmt.Printf("Worker %d stopped: %v\n", id, ctx.Err())
//			return
//		default:
//			fmt.Printf("Worker %d working\n", id)
//			time.Sleep(500 * time.Millisecond)
//		}
//	}
//}
