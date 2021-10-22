from mnist_training.src.main import main
import mnist_training.src.main


def test_main(mocker, minimal_dataloader):
    mocker.patch(
        'mnist_training.src.main.create_dataloader',
        return_value=minimal_dataloader
    )

    mocker.patch.object(mnist_training.src.main, "EPOCHS", 1)

    main()